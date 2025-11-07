# 1. 베이스 이미지 (Python 3.10)
FROM python

# 2. 컨테이너 내부 작업 디렉토리
WORKDIR /app

# 3. requirements 설치
RUN apt-get update && apt-get install -y git
