import cv2
import pytesseract
from yt_dlp import YoutubeDL
import os

# Tesseract 실행 파일 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# YouTube 영상 다운로드 함수
def download_youtube_video(youtube_url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return os.path.join(output_path, os.listdir(output_path)[0])

# 디렉토리 설정
video_output_path = './videos'
text_output_path = './extracted_text'
os.makedirs(video_output_path, exist_ok=True)
os.makedirs(text_output_path, exist_ok=True)

# 비디오 파일 경로
youtube_url = 'https://www.youtube.com/watch?v=Bv-VO6NFx2U'

video_path = download_youtube_video(youtube_url, video_output_path)

# 비디오 캡처 객체 생성
cap = cv2.VideoCapture(video_path)

frame_interval = 30  # 텍스트 추출을 위한 프레임 간격 설정
frame_count = 0

extracted_text = []

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break
    
    if frame_count % frame_interval == 0:
        # OCR을 사용하여 텍스트 추출
        text = pytesseract.image_to_string(frame, lang='eng')
        extracted_text.append(f"Frame {frame_count}:\n{text}\n{'-'*50}\n")
    
    frame_count += 1

cap.release()

# 추출된 텍스트를 파일로 저장
with open(os.path.join(text_output_path, 'extracted_text.txt'), 'w', encoding='utf-8') as f:
    f.writelines(extracted_text)

print("텍스트 추출이 완료되었습니다.")



# pip install opencv-python
# pip install pytesseract
# pip install pytube
# pip install yt-dlp
