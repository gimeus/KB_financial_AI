import openai
import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

# API 키 설정
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def ask_question(question, context):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Based on the following context, please answer the question:\n\nContext: {context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    with open('../data/summary.txt', 'r', encoding='utf-8') as f:
        summary_text = f.read()
    
    question = "What is the main content of this guidebook?"
    answer = ask_question(question, summary_text)
    print(f"Question: {question}")
    print(f"Answer: {answer}")