from openai import OpenAI
import sounddevice as sd
import numpy as np
import io
import os
from scipy.io.wavfile import write
from dotenv import load_dotenv
import time
import playsound
import pandas as pd
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import RunnableSequence
from langchain.llms import OpenAI as LangChainOpenAI

# 환경 변수에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# CSV 파일을 데이터프레임으로 로드
csv_files = {
    "베트남어": pd.read_csv("../../data/Dataset/financeData/processedData/베트남어_금융_가이드.csv"),
    "영어": pd.read_csv("../../data/Dataset/financeData/processedData/영어_금융_가이드.csv"),
    "중국어": pd.read_csv("../../data/Dataset/financeData/processedData/중국어_금융_가이드.csv"),
    "태국어": pd.read_csv("../../data/Dataset/financeData/processedData/태국어_금융_가이드.csv")
}

# 언어 선택 함수 (예: 입력 텍스트를 기반으로 언어를 추론)
def detect_language(user_input):
    # 여기서는 간단하게 예시로 영어를 사용합니다. 필요시 언어 감지 기능을 추가할 수 있습니다.
    if "vietnamese" in user_input.lower():
        return "베트남어"
    elif "chinese" in user_input.lower():
        return "중국어"
    elif "thai" in user_input.lower():
        return "태국어"
    else:
        return "영어"

# CSV 파일에서 관련 데이터를 검색하는 함수
def lookup_csv_data(user_input, language):
    df = csv_files.get(language)
    if df is not None:
        # CSV 파일에서 'Section' 열을 키워드로 사용
        for _, row in df.iterrows():
            if user_input.lower() in row['Section'].lower():
                return row['Summary']
    return "No relevant information found in the CSV."


# 음성 입력을 텍스트로 변환하는 함수 (Whisper 모델 사용)
def transcribe_audio_to_text(file_path):
    with open(file_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    return response.text  # Transcription 객체에서 텍스트 추출

# TTS를 통해 텍스트를 실시간으로 음성으로 변환하고 출력하는 함수
def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file("output.mp3")

# 실시간 오디오 입력을 처리하는 함수
def record_audio(duration=5, fs=16000):
    print("Recording", end="", flush=True)
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    
    for _ in range(duration):
        print(".", end="", flush=True)
        time.sleep(1)
    
    sd.wait()  # Wait until recording is finished
    print("\nRecording finished.")
    return audio_data

# LangChain과 GPT-4를 사용하여 응답을 생성하는 함수
def generate_response_with_langchain(user_input):
    # 언어를 감지하고 관련 CSV 파일에서 데이터를 검색
    language = detect_language(user_input)
    additional_info = lookup_csv_data(user_input, language)

    # LangChain의 PromptTemplate 사용
    prompt_template = PromptTemplate(
        input_variables=["input", "additional_info"],
        template="""
        You are a helpful assistant with expertise in financial guidance across multiple languages.
        User input: {input}
        Additional information from the database: {additional_info}
        Please provide a detailed response.
        """
    )

    # LLM 및 시퀀스 설정
    llm = LangChainOpenAI(api_key=api_key)
    chain = RunnableSequence([prompt_template, llm])

    # LangChain을 사용한 응답 생성
    return chain.invoke({"input": user_input, "additional_info": additional_info})

# 메인 대화 루프
while True:
    # 음성 입력을 녹음
    audio_data = record_audio()

    # 녹음된 데이터를 파일로 저장
    file_path = "temp_audio.wav"
    write(file_path, 16000, audio_data)  # WAV 형식으로 저장
    
    # Whisper 모델을 사용해 음성을 텍스트로 변환
    user_input = transcribe_audio_to_text(file_path)
    print(f"You said: {user_input}")

    # LangChain을 사용해 응답 생성
    gpt_reply = generate_response_with_langchain(user_input)
    print(f"GPT: {gpt_reply}")

    # TTS를 통해 텍스트를 실시간으로 출력
    text_to_speech(gpt_reply)
    # 생성된 음성을 재생
    playsound.playsound("output.mp3")
    # 생성된 음성 파일 삭제
    os.remove("output.mp3")
