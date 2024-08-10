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
def check_openai_connection():
    try:
        response = client.models.list()
        if response:
            print("OpenAI에 성공적으로 연결되었습니다.")
        return True
    except Exception as e:
        print(f"OpenAI 연결 오류: {e}")
        return False

def summarize_text(text):
    headers = {
        'Authorization': f'Bearer {client.api_key}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'model': 'gpt-4o',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': f'Please summarize the following text:\n\n{text}'}
        ],
    }

    try:
        response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        return summary
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return ""
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.text}")
        return ""
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ""

def read_and_process_text(input_file, output_file, chunk_size=50):
    summaries = []

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i in range(0, len(lines), chunk_size):
        chunk = ''.join(lines[i:i+chunk_size])
        print(f"\n처리 중인 텍스트 (줄 {i+1}부터 {i+chunk_size}까지):\n{chunk}")
        summary = summarize_text(chunk)
        summaries.append(summary)
        print(f"\n요약: {summary}")
        time.sleep(1)  # 요청 간에 약간의 지연을 추가하여 API 부담을 줄임

    full_summary = '\n\n'.join(summaries)
    
    # 요약 결과를 파일에 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_summary)
    print(f"요약 결과가 {output_file} 파일에 저장되었습니다.")

if __name__ == "__main__":
    if check_openai_connection():
        read_and_process_text('../data/cleaned_text.txt', '../data/summary.txt')
    print("모든 작업 완료.")
