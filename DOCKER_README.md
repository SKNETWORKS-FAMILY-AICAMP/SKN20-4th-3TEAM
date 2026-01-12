# Docker를 사용한 강아지 채팅 시스템

## 프로젝트 구조
```
SKN20-4th-3TEAM/
├── docker-compose.yml          # Docker Compose 설정
├── .dockerignore              # Docker 빌드 제외 파일
├── .env.example               # 환경 변수 예시
├── requirements.txt           # Python 패키지 목록
├── fastapi_backend/           # FastAPI 백엔드
│   ├── Dockerfile
│   ├── main.py
│   └── ...
└── django_frontend/           # Django 프론트엔드
    ├── Dockerfile
    ├── entrypoint.sh
    ├── manage.py
    └── ...
```

## 시작하기

### 1. 환경 변수 설정
```bash
# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 실제 값 입력
# - OPENAI_API_KEY: OpenAI API 키
# - DJANGO_SECRET_KEY: Django 시크릿 키
# - SECRET_KEY: JWT 시크릿 키
```

### 2. Docker 컨테이너 실행
```bash
# 모든 서비스 빌드 및 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f django
docker-compose logs -f fastapi
```

### 3. 서비스 접속
- **Django 프론트엔드**: http://localhost:8000
- **FastAPI 백엔드**: http://localhost:8001
- **FastAPI 문서**: http://localhost:8001/docs

### 4. Docker 컨테이너 관리
```bash
# 컨테이너 중지
docker-compose stop

# 컨테이너 시작 (이미 빌드된 경우)
docker-compose start

# 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 모두 삭제
docker-compose down -v

# 컨테이너 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart django
```

### 5. Django 관리 명령어 실행
```bash
# Django 마이그레이션
docker-compose exec django python manage.py migrate

# Django 슈퍼유저 생성
docker-compose exec django python manage.py createsuperuser

# Django 정적 파일 수집
docker-compose exec django python manage.py collectstatic

# Django 셸 접속
docker-compose exec django python manage.py shell
```

### 6. 컨테이너 내부 접속
```bash
# Django 컨테이너 bash 접속
docker-compose exec django bash

# FastAPI 컨테이너 bash 접속
docker-compose exec fastapi bash
```

## 개발 모드

Docker를 사용하지 않고 로컬에서 개발하려면:

### FastAPI 백엔드
```bash
cd fastapi_backend
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8001
```

### Django 프론트엔드
```bash
cd django_frontend
pip install -r ../requirements.txt
python manage.py runserver 8000
```

## 트러블슈팅

### 포트 충돌
이미 8000 또는 8001 포트를 사용 중이라면 `docker-compose.yml`에서 포트 변경:
```yaml
ports:
  - "다른포트:8000"  # 예: "8080:8000"
```

### 권한 문제 (Linux/Mac)
```bash
# entrypoint.sh 실행 권한 부여
chmod +x django_frontend/entrypoint.sh
```

### 데이터베이스 초기화
```bash
# 컨테이너와 볼륨 모두 삭제 후 재시작
docker-compose down -v
docker-compose up -d --build
```

### 패키지 업데이트
```bash
# requirements.txt 변경 후 재빌드
docker-compose up -d --build
```

## 주의사항
- `.env` 파일은 절대로 git에 커밋하지 마세요
- OpenAI API 키를 반드시 설정해야 RAG 시스템이 작동합니다
- 프로덕션 환경에서는 `DJANGO_DEBUG=False`로 설정하세요
- 볼륨을 통해 코드 변경사항이 자동으로 반영됩니다 (핫 리로드)
