from pathlib import Path
import httpx
from openai import OpenAI
from dotenv import load_dotenv
import os
# API 키 설정 및 클라이언트 생성
# .env 파일 로드
load_dotenv()

# API 키 설정 및 클라이언트 생성
api_key = os.getenv('OPENAI_API_KEY')
# OpenAI 클라이언트 설정
client = OpenAI(api_key=api_key)

# 음성 파일 저장 경로 설정
speech_file_path = Path(__file__).parent / "speech.mp3"

# 텍스트를 음성으로 변환 요청
url = "https://api.openai.com/v1/audio/speech"
headers = {
    "Authorization": f"Bearer {client.api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "tts-1",
    "voice": "alloy",
    "input": "Today is a wonderful day to build something people love!"
}

# 요청 및 파일 스트리밍
with httpx.stream("POST", url, headers=headers, json=data) as response:
    response.raise_for_status()
    with open(speech_file_path, 'wb') as file:
        for chunk in response.iter_bytes():
            file.write(chunk)
