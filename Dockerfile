# Python 3.9 slim 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (OpenAI 임베딩 사용으로 최소화)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app.py .
COPY .env .

# Chroma DB 디렉토리 생성
RUN mkdir -p /app/chroma_db

# 포트 노출
EXPOSE 8501

# Streamlit 애플리케이션 실행
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]