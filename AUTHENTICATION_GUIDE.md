# 🔐 JWT 토큰 기반 인증 아키텍처 가이드

## 📋 목차
1. [아키텍처 개요](#1-아키텍처-개요)
2. [인증 흐름](#2-인증-흐름)
3. [구현 상세](#3-구현-상세)
4. [파일 구조](#4-파일-구조)
5. [주요 변경사항](#5-주요-변경사항)
6. [문제 해결](#6-문제-해결)

---

## 1. 아키텍처 개요

### ✅ 최종 설계: JWT 토큰 기반 인증

```
사용자 요청
    ↓
┌─────────────────────────────────────────┐
│         Django Frontend                 │
│  - UI 렌더링 (HTML/CSS/JavaScript)    │
│  - JWT 토큰 세션 저장                  │
│  - FastAPI 호출 (토큰 자동 포함)       │
└─────────────────────────────────────────┘
    ↓ (Authorization: Bearer <token>)
┌─────────────────────────────────────────┐
│        FastAPI Backend                  │
│  - JWT 토큰 검증                        │
│  - 데이터베이스 처리                    │
│  - JSON 응답 반환                       │
└─────────────────────────────────────────┘
    ↓
  Database (SQLite/PostgreSQL)
```

### 왜 JWT인가?

| 특성 | Session | JWT ✅ |
|------|---------|--------|
| 저장소 | 서버 필요 | 클라이언트 (Stateless) |
| 확장성 | 분산 환경 어려움 | 마이크로서비스 친화적 |
| 모바일 | 약함 | 우수 |
| 간단성 | 중간 | 중간 |

---

## 2. 인증 흐름

### 🔄 로그인 프로세스

```
Step 1: Django 로그인 폼 제시
   └─ accounts/login.html 렌더링

Step 2: 사용자 입력
   └─ email, password 입력

Step 3: Django → FastAPI 로그인 요청
   requests.post(
     'http://localhost:8001/api/auth/login',
     json={'email': email, 'password': password}
   )

Step 4: FastAPI 처리
   ├─ 이메일 존재 확인
   ├─ 비밀번호 검증 (SHA256 해싱)
   ├─ JWT 토큰 생성
   │  payload = {"sub": email, "exp": datetime}
   └─ 토큰 반환
      {
        "access_token": "eyJhbGc...",
        "token_type": "bearer"
      }

Step 5: Django 세션 저장
   request.session['access_token'] = token
   request.session['user_email'] = email
   request.session.modified = True

Step 6: Django 로그인 (선택사항)
   └─ Django User 생성/조회 후 로그인
      (Django 미들웨어 호환성 유지용)

Step 7: 리다이렉트
   └─ dogs:profile_select 페이지로 이동
```

### 🔄 API 요청 프로세스

```
Step 1: Django의 FastAPI API 호출
   └─ GET /api/dogs/
      headers={'Authorization': f'Bearer {token}'}

Step 2: FastAPI JWT 검증
   ├─ Authorization 헤더에서 토큰 추출
   ├─ 토큰 검증 (get_current_user_email)
   │  └─ JWT 서명 확인
   │  └─ 만료 시간 확인
   ├─ 사용자 정보 조회 (get_current_user)
   │  └─ 이메일로 User 모델 조회
   └─ 로직 실행

Step 3: FastAPI 응답
   └─ JSON 데이터 반환

Step 4: Django 응답 처리
   └─ 템플릿 렌더링
```

### 🚪 로그아웃 프로세스

```
Step 1: 로그아웃 요청
   └─ /accounts/logout/

Step 2: Django 세션 제거
   del request.session['access_token']
   del request.session['user_email']

Step 3: Django 로그아웃
   logout(request)

Step 4: 리다이렉트
   └─ 랜딩 페이지로 이동
```

---

## 3. 구현 상세

### 📁 FastAPI: auth_utils.py (공통 인증 유틸)

```python
# 목적: JWT 검증 로직 중앙화

from fastapi import Header, HTTPException, status, Depends
from jose import jwt

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

def get_current_user_email(authorization: str = Header(...)) -> str:
    """
    Authorization 헤더에서 JWT 토큰 추출 및 검증
    
    사용법:
      email = Depends(get_current_user_email)
    """
    # "Bearer <token>" 형식 파싱
    token = authorization[7:]  # "Bearer " 제거
    
    # JWT 토큰 검증
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        return email
    except JWTError:
        raise HTTPException(status_code=401)

def get_current_user(email: str = Depends(get_current_user_email), ...) -> User:
    """
    JWT에서 추출한 이메일로 사용자 조회
    
    사용법:
      current_user = Depends(get_current_user)
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401)
    return user
```

### 📁 FastAPI: routers/dogs.py (간단해진 인증)

**이전 (복잡):**
```python
@router.get("/")
def get_dog_profiles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # 직접 검증
):
    email = current_user["email"]
    user = db.query(User).filter(User.email == email).first()
    # ... 반복되는 코드
```

**현재 (간단):**
```python
from auth_utils import get_current_user

@router.get("/")
def get_dog_profiles(
    current_user: User = Depends(get_current_user)  # 이미 검증된 User 객체
):
    profiles = db.query(DogProfile).filter(
        DogProfile.owner_id == current_user.id
    ).all()
    return profiles
```

**개선 사항:**
- ✅ 코드 중복 제거
- ✅ 타입 안정성 (User 객체)
- ✅ 유지보수 용이
- ✅ 테스트 간편

### 📁 Django: accounts/views.py (토큰 관리)

```python
def login_view(request):
    """로그인"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # FastAPI에 로그인 요청
        response = requests.post(
            f'{settings.FASTAPI_BASE_URL}/api/auth/login',
            json={'email': email, 'password': password}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # ✅ JWT 토큰을 Django 세션에 저장
            request.session['access_token'] = data['access_token']
            request.session['user_email'] = email
            request.session.modified = True
            
            # Django User (Django 미들웨어 호환용)
            user, _ = User.objects.get_or_create(
                username=email,
                defaults={'email': email}
            )
            login(request, user)
            
            return redirect('dogs:profile_select')
```

### 📁 Django: 다른 views에서 토큰 사용

```python
def dogs_profile_view(request):
    """강아지 프로필 조회"""
    # 세션에서 토큰 자동 조회
    token = request.session.get('access_token')
    
    # FastAPI 호출 (토큰 자동 포함)
    response = requests.get(
        f'{settings.FASTAPI_BASE_URL}/api/dogs/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        dogs = response.json()
        return render(request, 'dogs/list.html', {'dogs': dogs})
```

---

## 4. 파일 구조

```
fastapi_backend/
├── auth_utils.py                    ✨ NEW: 공통 JWT 검증 유틸
├── routers/
│   ├── auth.py                     📝 수정: 토큰 생성만 담당
│   ├── dogs.py                     📝 수정: auth_utils 사용
│   └── chat.py                     📝 수정: auth_utils 사용
├── models.py                        (변경 없음)
├── schemas.py                       (변경 없음)
├── database.py                      (변경 없음)
└── main.py                          (변경 없음)

django_frontend/
├── config/
│   └── settings.py                 📝 수정: JWT 시크릿 키 추가 (향후용)
├── accounts/
│   └── views.py                    📝 수정: 토큰 기반 인증
├── dogs/
│   └── views.py                    📝 수정: 토큰 자동 포함
├── chat/
│   └── views.py                    📝 수정: 토큰 자동 포함
└── templates/                       (변경 없음)
```

---

## 5. 주요 변경사항

### 🔧 Change 1: FastAPI 인증 통일

**파일:** `fastapi_backend/auth_utils.py`
- ✅ 새로 생성
- 목적: JWT 검증 로직 중앙화
- 사용: 모든 라우터에서 import

```python
from auth_utils import get_current_user, get_current_user_email
```

### 🔧 Change 2: FastAPI 라우터 간단화

**파일:** `fastapi_backend/routers/dogs.py`, `chat.py`
- ✅ JWT 검증 코드 제거 (auth_utils로 이동)
- ✅ 반복 코드 제거 (이메일 → User 조회 제거)
- ✅ 타입 안정성 개선 (dict → User 객체)

```python
# Before
def get_dog_profiles(current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    user = db.query(User).filter(User.email == email).first()

# After
def get_dog_profiles(current_user: User = Depends(get_current_user)):
    profiles = db.query(DogProfile).filter(
        DogProfile.owner_id == current_user.id
    ).all()
```

### 🔧 Change 3: Django 로그인 로직 정리

**파일:** `django_frontend/accounts/views.py`
- ✅ Django User 생성 유지 (Django 미들웨어 호환)
- ✅ JWT 토큰 세션 저장 (FastAPI 호출용)
- ✅ 명확한 코멘트 추가

```python
# JWT 토큰을 Django 세션에 저장
request.session['access_token'] = data['access_token']
request.session['user_email'] = email

# Django User (미들웨어 호환용)
user, _ = User.objects.get_or_create(...)
login(request, user)
```

---

## 6. 문제 해결

### ❌ 문제 1: "토큰이 없습니다" 에러

**원인:** 세션에 access_token이 저장되지 않음

**해결:**
```python
# ✅ 반드시 해야 할 일
request.session['access_token'] = token
request.session.modified = True  # 명시적 저장
```

### ❌ 문제 2: "토큰이 유효하지 않습니다" 에러

**원인:**
1. SECRET_KEY가 다름 (auth.py vs auth_utils.py)
2. 토큰이 만료됨
3. Authorization 헤더 형식 잘못

**해결:**
```python
# 1. SECRET_KEY 확인
# fastapi_backend/routers/auth.py
# fastapi_backend/auth_utils.py
# ⚠️ 둘 다 동일해야 함!

# 2. 토큰 만료 확인
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 1일

# 3. Authorization 헤더 확인
# ✅ 올바른 형식: "Bearer eyJhbGc..."
```

### ❌ 문제 3: Django @login_required 작동 안 함

**원인:** Django User 모델에 저장되지 않음

**해결:**
```python
# ✅ login() 함수 호출 필수
login(request, user, backend='django.contrib.auth.backends.ModelBackend')

# 그러면 @login_required 작동
@login_required
def some_view(request):
    pass  # OK!
```

### ❌ 문제 4: "다른 사용자의 강아지와는 채팅할 수 없습니다" 에러

**원인:** JWT의 사용자와 강아지 owner_id 불일치

**해결:**
```python
# ✅ FastAPI는 owner_id 검증
dog = db.query(DogProfile).filter(
    DogProfile.id == dog_id,
    DogProfile.owner_id == current_user.id  # 소유자 확인
).first()

if not dog:
    raise HTTPException(status_code=403)  # 403 Forbidden
```

---

## 🎯 체크리스트

### 설치 및 실행

```bash
# FastAPI 실행
cd fastapi_backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001

# Django 실행
cd django_frontend
python manage.py runserver 8000
```

### 테스트

```bash
# 1. 회원가입
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"test123"}'

# 2. 로그인 (토큰 얻기)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# 3. 토큰으로 API 호출
curl -X GET http://localhost:8001/api/dogs/ \
  -H "Authorization: Bearer <your_token_here>"
```

### 배포 전 체크리스트

- [ ] SECRET_KEY 환경변수로 변경 (프로덕션)
- [ ] SESSION_COOKIE_SECURE = True (HTTPS 필수)
- [ ] ALLOWED_HOSTS 설정
- [ ] DEBUG = False (프로덕션)
- [ ] 데이터베이스 통합 (단일 DB)
- [ ] JWT 토큰 만료 시간 적절히 설정

---

## 📚 참고 자료

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT 이해하기](https://jwt.io/introduction)
- [Django Sessions](https://docs.djangoproject.com/en/stable/topics/http/sessions/)

---

**작성일:** 2025-01-08
**마지막 수정:** 2025-01-08

