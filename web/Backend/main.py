from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 요청을 허용할 도메인
    allow_credentials=True,
    allow_methods=["*"],  # 허용할 HTTP 메소드
    allow_headers=["*"],  # 허용할 HTTP 헤더
)

# MySQL 데이터베이스 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",  # MySQL 사용자 이름
    password="1234",  # MySQL 비밀번호
    database="chatbot_db"  # 데이터베이스 이름
)

# 데이터베이스에 저장할 데이터 모델 정의
class Message(BaseModel):
    type: str
    text: str
    time: str

@app.post("/messages/")
def save_message(message: Message):
    cursor = db.cursor()
    sql = "INSERT INTO messages (type, text, time) VALUES (%s, %s, %s)"
    val = (message.type, message.text, message.time)
    try:
        cursor.execute(sql, val)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save message to DB")
    finally:
        cursor.close()

    return {"message": "Message stored successfully"}
