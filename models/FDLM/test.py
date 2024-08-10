from openai import OpenAI
import os
import pandas as pd
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 설정 및 클라이언트 생성
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# 미리 로드된 CSV 데이터를 저장할 딕셔너리
loaded_data = {}

def check_openai_connection():
    try:
        response = client.models.list()
        if response:
            print("OpenAI에 성공적으로 연결되었습니다.")
        return True
    except Exception as e:
        print(f"OpenAI 연결 오류: {e}")
        return False

def load_csv_data(csv_file):
    """CSV 파일을 로드하고 데이터를 데이터프레임으로 반환."""
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        print(f"CSV 파일 로드 오류: {e}")
        return None

def filter_data(df, keywords):
    """주어진 키워드를 사용해 데이터프레임 필터링."""
    mask = df.apply(lambda row: row.astype(str).str.contains('|'.join(keywords), case=False).any(), axis=1)
    filtered_df = df[mask]
    return filtered_df.to_string(index=False)

def query_csv_data(context, question, chunk_size=100):
    """필터링된 데이터를 기반으로 OpenAI API를 사용해 질의에 응답."""
    summaries = []
    for i in range(0, len(context), chunk_size):
        chunk = context[i:i + chunk_size]
        prompt = f"Here is some context from the data:\n{chunk}\n\nQuestion: {question}\nAnswer:"

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Keep responses very short and concise. Expand only if asked."},
                    {"role": "user", "content": prompt}
                ]
            )
            summary = response.choices[0].message.content.strip()
            summaries.append(summary)
        except Exception as e:
            print(f"OpenAI 요청 오류: {e}")
            summaries.append("[Error]")

    return ' '.join(summaries)

def main():
    if not check_openai_connection():
        return

    # 각 언어별로 CSV 파일을 로드하여 메모리에 저장
    csv_files = [
        ("../../data/Dataset/financeData/processedData/베트남어_금융_가이드.csv", "베트남어"),
        ("../../data/Dataset/financeData/processedData/영어_금융_가이드.csv", "영어"),
        ("../../data/Dataset/financeData/processedData/중국어_금융_가이드.csv", "중국어"),
        ("../../data/Dataset/financeData/processedData/태국어_금융_가이드.csv", "태국어")
    ]

    for csv_file, language in csv_files:
        print(f"\n{language} CSV 파일을 로드 중입니다: {csv_file}")
        df = load_csv_data(csv_file)
        if df is not None:
            loaded_data[language] = df
        else:
            print(f"{language} CSV 데이터를 로드하는 데 실패했습니다.")
            return

    while True:
        language = input("\n질문할 언어를 선택하세요 (베트남어, 영어, 중국어, 태국어) 또는 '종료'를 입력하세요: ")
        if language == '종료':
            break
        if language not in loaded_data:
            print(f"{language}에 대한 데이터가 로드되지 않았습니다.")
            continue

        question = input(f"{language} 데이터에 대해 질문을 입력하세요: ")
        keywords = question.split()  # 질문을 키워드로 분할
        filtered_context = filter_data(loaded_data[language], keywords)

        if filtered_context.strip():  # 필터된 데이터가 비어있지 않으면
            answer = query_csv_data(filtered_context, question)
            if answer:
                print(f"\n{language}에 대한 답변: {answer}")
            else:
                print("응답을 생성하는 데 실패했습니다.")
        else:
            print("관련된 데이터를 찾지 못했습니다.")

if __name__ == "__main__":
    main()
