from openai import OpenAI
import sounddevice as sd
import numpy as np
import io
import os
from scipy.io.wavfile import write
from dotenv import load_dotenv
import time
import playsound

# 환경 변수에서 API 키 로드
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
# OpenAI 클라이언트 설정

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

def generate_response(prompt):
    response = client.chat.completions.create(
    model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": prompt}
        ]
    )
    # 디버깅을 위한 print 문 추가
    message = response.choices[0].message
    if isinstance(message, dict):
        return message.get('content', '')
    else:
        return message.content

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

    gpt_reply = generate_response(user_input)
    print(f"GPT: {gpt_reply}")

    # TTS를 통해 텍스트를 실시간으로 출력
    text_to_speech(gpt_reply)
    # 생성된 음성을 재생
    playsound.playsound("output.mp3")
    # 생성된 음성 파일 삭제
    os.remove("output.mp3")


