# # src/extract_text.py
# import pdfplumber
# import re

# def remove_unusual_line_terminators(text):
#     # 비정상적인 줄 종결자를 정규 표현식으로 찾습니다.
#     cleaned_text = re.sub(r'\u2028|\u2029', '', text)
#     return cleaned_text

# def extract_text_from_pdf(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         full_text = ''
#         for page in pdf.pages:
#             full_text += page.extract_text() + '\n'
#     return full_text

# if __name__ == "__main__":
#     pdf_path = '../data/data1.pdf'
#     text = extract_text_from_pdf(pdf_path)
#     cleaned_text = remove_unusual_line_terminators(text)
    
#     with open('../data/cleaned_text.txt', 'w', encoding='utf-8') as f:
#         f.write(cleaned_text)
#     print("텍스트 추출 및 비정상적인 줄 종결자 제거 완료.")

import pdfplumber
import re
import os

def remove_unusual_line_terminators(text):
    # 비정상적인 줄 종결자를 정규 표현식으로 찾습니다.
    cleaned_text = re.sub(r'\u2028|\u2029', '', text)
    return cleaned_text

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                full_text += extracted_text + '\n'
            else:
                print(f"텍스트를 추출할 수 없습니다: {pdf_path}, 페이지: {page.page_number}")
    return full_text

def process_pdfs_to_text():
    # PDF 파일 경로와 저장할 텍스트 파일 경로
    pdf_files = [
        ("../../data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_베트남어_낱장.pdf", "../../data/Dataset/financeData/txtData/pdf_cleaned_text_베트남어.txt"),
        ("../../data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_영어_낱장.pdf", "../../data/Dataset/financeData/txtData/pdf_cleaned_text_영어.txt"),
        ("../../data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_중국어_낱장.pdf", "../../data/Dataset/financeData/txtData/pdf_cleaned_text_중국어.txt"),
        ("../../data/Dataset/financeData/originData/외국인을 위한 금융생활 가이드북_태국어_낱장.pdf", "../../data/Dataset/financeData/txtData/pdf_cleaned_text_태국어.txt")
    ]

    for pdf_path, text_path in pdf_files:
        text = extract_text_from_pdf(pdf_path)
        cleaned_text = remove_unusual_line_terminators(text)
        
        # 텍스트를 파일로 저장
        os.makedirs(os.path.dirname(text_path), exist_ok=True)
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"텍스트 추출 및 비정상적인 줄 종결자 제거 완료: {text_path}")

if __name__ == "__main__":
    process_pdfs_to_text()

