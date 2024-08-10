from pathlib import Path
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
# OpenAI API 키 설정
# openai.api_key = 'YOUR_API_KEY'

# 음성 파일 저장 경로 설정
speech_file_path = Path(__file__).parent / "speech.mp3"

# 텍스트를 음성으로 변환 요청
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Today is a wonderful day to build something people love!",
)

response.stream_to_file(speech_file_path)
