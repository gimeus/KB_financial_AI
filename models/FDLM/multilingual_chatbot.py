import pandas as pd
import random
from openai import OpenAI
import sounddevice as sd
import numpy as np
import os
from scipy.io.wavfile import write
from dotenv import load_dotenv
import time
import playsound
from fuzzywuzzy import fuzz
import mysql.connector
from datetime import datetime

# 환경 변수에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# CSV 파일을 데이터프레임으로 로드
csv_file = pd.read_csv("../../data/Dataset/financeData/processedData/Combined_FAQ.csv")

# MySQL 데이터베이스 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="chatbot_db"
)

# 사용자 입력을 데이터베이스에 저장하는 함수
def save_message_to_db(message_type, message_text):
    cursor = db.cursor()
    sql = "INSERT INTO messages (type, text, time) VALUES (%s, %s, %s)"
    val = (message_type, message_text, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        cursor.execute(sql, val)
        db.commit()
        print(f"{message_type.capitalize()} message saved to DB: {message_text}")
    except Exception as e:
        db.rollback()
        print(f"Failed to save message to DB: {e}")
    finally:
        cursor.close()

# 음성 입력을 텍스트로 변환하는 함수 (Whisper 모델 사용)
def transcribe_audio_to_text(file_path, language):
    with open(file_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language  # 선택된 언어를 사용
        )
    return response.text  # Transcription 객체에서 텍스트 추출

# TTS를 통해 텍스트를 실시간으로 음성으로 변환하고 출력하는 함수
def text_to_speech(text, language):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file("output.mp3")
    playsound.playsound("output.mp3")
    os.remove("output.mp3")

# 실시간 오디오 입력을 처리하는 함수
def record_audio(duration=10, fs=16000):
    print("Recording", end="", flush=True)
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    
    for _ in range(duration):
        print(".", end="", flush=True)
        time.sleep(1)
    
    sd.wait()  # Wait until recording is finished
    print("\nRecording finished.")
    return audio_data

def get_relevant_context(prompt):
    best_match = None
    highest_ratio = 0
    
    for _, row in csv_file.iterrows():
        question = row['Question']
        ratio = fuzz.partial_ratio(prompt.lower(), question.lower())
        
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = row
    
    if best_match is not None and highest_ratio > 70:  # 70% 이상의 유사도를 기준으로 매칭
        section = best_match['Section']
        question = best_match['Question']
        answer = best_match['Answer']
        return f"Section: {section}\nQuestion: {question}\nAnswer: {answer}"
    else:
        return "No relevant data found."

def generate_response(prompt, language):
    context = get_relevant_context(prompt)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are an assistant for helping foreigners in Korea. Use the following information to respond: {context}"},
            {"role": "user", "content": prompt}
        ]
    )
    message = response.choices[0].message
    if isinstance(message, dict):
        return message.get('content', '')
    else:
        return message.content

# 언어 선택 및 초기 질문
def select_language():
    language_prompt = (
        "Please select a language:\n"
        "Number 1: English\n"
        "第二个是中文 (Number 2: Chinese)\n"
        "Số 3: Tiếng Việt (Number 3: Vietnamese)\n"
        "หมายเลข 4: ภาษาไทย (Number 4: Thai)\n"
    )
    text_to_speech(language_prompt, "en")  # 기본 음성으로 질문
    choice = input("Enter the number of the language you want to use: ")
    
    if choice == '1':
        return "en"
    elif choice == '2':
        return "zh"
    elif choice == '3':
        return "vi"
    elif choice == '4':
        return "th"
    else:
        print("Invalid choice. Defaulting to English.")
        return "en"

# 메인 대화 루프
language = select_language()  # 언어 선택

while True:
    # 음성 입력을 녹음
    audio_data = record_audio()

    # 녹음된 데이터를 파일로 저장
    file_path = "temp_audio.wav"
    write(file_path, 16000, audio_data)  # WAV 형식으로 저장
    
    # Whisper 모델을 사용해 음성을 텍스트로 변환
    user_input = transcribe_audio_to_text(file_path, language)
    print(f"You said: {user_input}")

    # 사용자 입력을 데이터베이스에 저장
    save_message_to_db('user', user_input)

    # GPT 모델에 입력을 전달하여 응답 생성
    gpt_reply = generate_response(user_input, language)
    print(f"GPT: {gpt_reply}")

    # GPT 응답을 데이터베이스에 저장
    save_message_to_db('gpt', gpt_reply)

    # TTS를 통해 텍스트를 실시간으로 출력
    text_to_speech(gpt_reply, language)
