import cv2
import pytesseract
from yt_dlp import YoutubeDL
import os

# Tesseract 실행 파일 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def download_youtube_video(youtube_url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    return os.path.join(output_path, os.listdir(output_path)[0])

def process_videos_for_language(language, video_urls, output_path):
    extracted_text = []
    for youtube_url in video_urls:
        video_path = download_youtube_video(youtube_url, output_path)

        cap = cv2.VideoCapture(video_path)
        frame_interval = 30  # 텍스트 추출을 위한 프레임 간격 설정
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                text = pytesseract.image_to_string(frame, lang='eng')
                extracted_text.append(f"Frame {frame_count}:\n{text}\n{'-'*50}\n")

            frame_count += 1

        cap.release()

    text_file_path = os.path.join(output_path, f'youtube_cleaned_text_{language}.txt')
    with open(text_file_path, 'w', encoding='utf-8') as f:
        f.writelines(extracted_text)
    print(f"{language} 언어의 텍스트 추출이 완료되었습니다: {text_file_path}")

def main():
    video_output_path = '../../data/Dataset/financeData/'
    text_output_path = '../../data/Dataset/financeData/txtData/'
    os.makedirs(video_output_path, exist_ok=True)
    os.makedirs(text_output_path, exist_ok=True)
    
    links_file_path = '../../data/Dataset/financeData/youtube_links.txt'  # youtube_links.txt 파일의 경로 설정
    language = None
    video_urls = []

    with open(links_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("#"):
                if language and video_urls:
                    process_videos_for_language(language, video_urls, text_output_path)
                language = line[1:]
                video_urls = []
            else:
                video_urls.append(line)

    if language and video_urls:
        process_videos_for_language(language, video_urls, text_output_path)

if __name__ == "__main__":
    main()





# pip install opencv-python
# pip install pytesseract
# pip install pytube
# pip install yt-dlp
