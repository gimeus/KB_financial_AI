from openai import OpenAI
import time
import json
import os
import httpx
from dotenv import load_dotenv

# API 키 설정 및 클라이언트 생성
# .env 파일 로드
load_dotenv()

# API 키 설정 및 클라이언트 생성
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
model_link = 'finance'  # 모델 링크

def call_custom_gpt(messages):
    response = client.chat.completions.create(
        model=model_link,
        messages=messages
    )
    return response['choices'][0]['message']['content']


# 예제 메시지
messages = [
    {"role": "system", "content": "You are an AI guide designed to provide accurate information in the language spoken by foreigners who are visiting Korea."},
    {"role": "user", "content": "我现在在安山，附近有外国人专用银行吗？"}
]

# OpenAI 호출
response = call_custom_gpt(messages)
print(response)