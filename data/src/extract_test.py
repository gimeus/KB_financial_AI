# src/extract_text.py
import pdfplumber
import re

def remove_unusual_line_terminators(text):
    # 비정상적인 줄 종결자를 정규 표현식으로 찾습니다.
    cleaned_text = re.sub(r'\u2028|\u2029', '', text)
    return cleaned_text

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text() + '\n'
    return full_text

if __name__ == "__main__":
    pdf_path = '../data/data1.pdf'
    text = extract_text_from_pdf(pdf_path)
    cleaned_text = remove_unusual_line_terminators(text)
    
    with open('../data/cleaned_text.txt', 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    print("텍스트 추출 및 비정상적인 줄 종결자 제거 완료.")
