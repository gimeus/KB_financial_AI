
영상 데이터 처리를 위해선
pytesseract 를 다운받아서 
C:\Program Files\Tesseract-OCR\tesseract.exe'
이 경로에 두고 path 처리 해야합니다.

KB_financial_AI\models\FDLM> 
이 경로에서 실행하면 mp4 유튜브 링크의 mp4 파일이 생성됩니다. 이는 .gitgnore에 막혀있습니다.
직접 실행하시면 다운로드가 되는 것을 확인할 수 있습니다.
 
 python extract_text_from_video.py

.env 폴더를 FDLM 안에 넣어놨습니다. 여기서
OPENAI_API_KEY=본인키
이 형태로 저장해야합니다.

금융데이터는 2가지 데이터(금감원자료) 전처리를 가진다.
-1.영상 데이터 전처리는 2가지 과정
-- 
-2.Pdf 데이터 전처리 과정
--현재 총 4개국 금감원 교재 pdf가 있다. 이를 전처리한다
