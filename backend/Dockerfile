FROM python:3.11-slim

# 작업 디렉토리를 /app으로 깔끔하게 설정
WORKDIR /app

# 1. requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. backend 폴더 내부의 모든 파일(app 폴더 전체 포함)을 현재 작업 디렉토리(/app)로 복사
COPY . .

# 3. uvicorn이 실행할 때 현재 디렉토리 기준 'app.main:app'을 실행하도록 설정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]