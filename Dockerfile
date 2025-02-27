# 베이스 이미지로 Python 3.9 사용
FROM python:3.12.1 

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일들을 컨테이너로 복사
COPY requirements.txt ./
COPY . ./

# 의존성 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 서버 실행
CMD ["python", "server.py"]

