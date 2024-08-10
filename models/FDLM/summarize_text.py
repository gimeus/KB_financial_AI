from openai import OpenAI
import time
import json
import pandas as pd
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

def summarize_text_chunked(text, language, chunk_size=3000):
    headers = {
        'Authorization': f'Bearer {client.api_key}',
        'Content-Type': 'application/json',
    }
    summaries = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        json_data = {
            'model': 'gpt-4o',
            'messages': [
                {'role': 'system', 'content': f'You are a helpful assistant. Please respond in {language}.'},
                {'role': 'user', 'content': f'Please summarize the following text:\n\n{chunk}'}
            ],
        }

        try:
            response = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            summaries.append(summary)
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            summaries.append("[Request error]")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.text}")
            summaries.append("[HTTP error]")
        except Exception as e:
            print(f"Unexpected error: {e}")
            summaries.append("[Unexpected error]")

    # 청크 요약을 모두 결합
    return ' '.join(summaries)

def process_text_to_csv(input_file, output_file, language):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    summary = summarize_text_chunked(text, language)
    
    # CSV로 저장하기 위해 데이터프레임 생성
    df = pd.DataFrame([{'Section': 'General', 'Summary': summary}])
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"요약 결과가 {output_file} 파일에 저장되었습니다.")

if __name__ == "__main__":
    if check_openai_connection():
        # 각 언어별로 텍스트 파일을 읽어와서 요약 후 CSV로 저장
        text_files = [
            ("../../data/Dataset/financeData/txtData/cleaned_text_베트남어.txt", "../../data/Dataset/financeData/processedData/베트남어_금융_가이드.csv", "Vietnamese"),
            ("../../data/Dataset/financeData/txtData/cleaned_text_영어.txt", "../../data/Dataset/financeData/processedData/영어_금융_가이드.csv", "English"),
            ("../../data/Dataset/financeData/txtData/cleaned_text_중국어.txt", "../../data/Dataset/financeData/processedData/중국어_금융_가이드.csv", "Chinese"),
            ("../../data/Dataset/financeData/txtData/cleaned_text_태국어.txt", "../../data/Dataset/financeData/processedData/태국어_금융_가이드.csv", "Thai")
        ]

        for text_file, csv_file, language in text_files:
            process_text_to_csv(text_file, csv_file, language)
        print("모든 작업 완료.")