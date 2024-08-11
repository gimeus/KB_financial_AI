import subprocess
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
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",  # MySQL 사용자 이름
        password="1234",  # MySQL 비밀번호
        database="chatbot_db"  # 데이터베이스 이름
    )
    print("Database connection successful")
except mysql.connector.Error as err:
    print(f"Error: {err}")
    db = None

# 데이터베이스에 저장할 데이터 모델 정의
class Message(BaseModel):
    type: str
    text: str
    time: str

@app.get("/test-db/")
def test_db():
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    return {"message": "Database connection successful"}

@app.post("/messages/")
def save_message(message: Message):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
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

# test3.py를 실행하는 엔드포인트 추가
@app.post("/start-recording")
def start_recording():
    try:
        # test3.py 스크립트를 실행
        subprocess.Popen(["python", "../../models/FDLM/test3.py"])
        return {"message": "Recording started"}
    except Exception as e:
        return {"message": f"Error: {e}"}
