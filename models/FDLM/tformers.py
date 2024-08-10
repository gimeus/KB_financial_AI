import pdfplumber
import pytesseract
from PIL import Image
import re
import pandas as pd
import os
import time
import httpx
from dotenv import load_dotenv
from openai import OpenAI

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

def summarize_text(text, language):
    headers = {
        'Authorization': f'Bearer {client.api_key}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'model': 'gpt-4',
        'messages': [
            {'role': 'system', 'content': f'You are a helpful assistant. Please respond in {language}.'},
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

def extract_text_from_pdf(pdf_path, lang='eng'):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            # 텍스트 추출
            text = page.extract_text()
            if text:
                full_text += text + '\n'
            # 이미지에서 텍스트 추출
            for image in page.images:
                img_cropped = page.within_bbox(image['bbox']).to_image()
                img_pil = Image.open(img_cropped.stream)
                img_text = pytesseract.image_to_string(img_pil, lang=lang)
                full_text += img_text + '\n'
    return full_text

def clean_text(text):
    text = re.sub(r'\u2028|\u2029', '', text)
    lines = text.split('\n')
    lines = list(dict.fromkeys(lines))
    cleaned_text = ' '.join(lines)
    return cleaned_text

def create_csv_from_pdf(pdf_path, csv_path, lang_code, language):
    text = extract_text_from_pdf(pdf_path, lang=lang_code)
    cleaned_text = clean_text(text)
    
    # 텍스트를 요약할 때 해당 언어로 요약
    summary = summarize_text(cleaned_text, language)

    df = pd.DataFrame([{'Section': 'General', 'Summary': summary}])
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"CSV 파일이 {csv_path}에 저장되었습니다.")

if __name__ == "__main__":
    if check_openai_connection():
        pdf_files = [
            ("C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_베트남어_낱장.pdf", 
             "C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/processedData/베트남어_금융_가이드.csv", 'vie', 'Vietnamese'),
            ("C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_영어_낱장.pdf", 
             "C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/processedData/영어_금융_가이드.csv", 'eng', 'English'),
            ("C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_중국어_낱장.pdf", 
             "C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/processedData/중국어_금융_가이드.csv", 'chi_sim', 'Chinese'),
            ("C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_태국어_낱장.pdf", 
             "C:/Users/user/Documents/GitHub/KB_financial_AI/data/Dataset/financeData/processedData/태국어_금융_가이드.csv", 'tha', 'Thai')
        ]

        for pdf_file, csv_file, lang_code, language in pdf_files:
            create_csv_from_pdf(pdf_file, csv_file, lang_code, language)
        print("모든 작업 완료.")
