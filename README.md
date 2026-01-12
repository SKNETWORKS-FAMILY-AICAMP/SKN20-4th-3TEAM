# 🐾 Dr. 멍 - RAG 기반 반려견 건강 상담 챗봇

<div align="center">

**당신의 반려견에게 맞춤 상담을 제공하는 AI 수의사**

[![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

</div>

## 👥 팀원 소개

<div align="center">
<table>
  <tr>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/85e707e3-380e-4b47-a530-cc593bcd4f87" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>박찬</b><br>팀장
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/40307edb-2139-4c87-923a-a18ce394f5b0" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>김나현</b><br>팀원
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/806b67c5-b5a0-4605-868b-bf52895bc006" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>이도경</b><br>팀원
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/5c1c0ded-8509-412e-9d51-46d8bd9e7c11" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>안채연</b><br>팀원
      </div>
    </td>
    <td align="center" width="150" style="vertical-align: top; padding: 10px;">
      <img src="https://github.com/user-attachments/assets/334057f7-b2a3-4fac-919c-d78ade2be0fe" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
      <div style="margin-top: 8px;">
        <b>이경현</b><br>팀원
      </div>
    </td>
  </tr>
</table>
</div>

---

## 📑 목차
1. [프로젝트 개요](#-프로젝트-개요)
2. [문제 정의 및 목표](#-문제-정의-및-목표)
3. [주요 기능](#-주요-기능)
4. [기술 스택](#-기술-스택)
5. [시스템 아키텍처](#-시스템-아키텍처)
6. [ERD 다이어그램](#-erd-다이어그램)
7. [핵심 구현 내용](#-핵심-구현-내용)
8. [프로젝트 성과](#-프로젝트-성과)

---

## 🎯 프로젝트 개요

### 프로젝트 정보
- **프로젝트명**: Dr. 멍
- **개발 기간**: 3차(RAG 챗봇) + 4차(웹 서비스) 통합 프로젝트
- **팀 구성**: 5명
- **개발 환경**: Python 3.11+, SQLite

### 프로젝트 배경
반려동물 보호자들은 인터넷에서 신뢰할 수 있는 수의학 정보를 찾기 어렵고, 검색 엔진은 키워드 중심이라 반려견의 개별 상황을 고려한 상담이 불가능합니다. 또한 상담 시마다 반려견 정보를 반복 입력해야 하는 불편함이 존재했습니다.

---

## 💡 문제 정의 및 목표

### 단계별 문제 해결

#### 3차 프로젝트: RAG 기반 챗봇 개발
**문제점**
- 인터넷의 검증되지 않은 수의학 정보
- 키워드 기반 검색의 맥락 부재

**해결 방안**
- 수의학 서적, 논문, 실제 상담 데이터 기반 RAG 시스템 구축
- 질문 → 벡터 검색 → 관련 문서 조회 → 답변 생성 파이프라인

**발견된 한계**
- ❌ 매번 반려견 정보(나이, 견종, 질환 등)를 수동 입력
- ❌ 이전 대화 기억 불가
- ❌ 개인화 불가능

#### 4차 프로젝트: 개인화 웹 서비스 구축
**목표**
> "사용자가 반려견 정보를 반복 입력하지 않아도, 시스템이 자동으로 프로필을 반영하여 맞춤형 상담을 제공하는 웹 서비스"

**핵심 가치**
- ✅ 프로필 자동 반영으로 사용자 편의성 향상
- ✅ 반려견 개별 특성(나이, 견종, 질환) 고려한 맞춤 답변
- ✅ 반려견별 대화 히스토리 관리
- ✅ 검증된 출처 기반 신뢰성 확보

---

## 🎨 주요 기능

### 1. 사용자 인증 시스템
- **회원가입/로그인**: JWT 토큰 기반 인증
- **비밀번호 재설정**: 안전한 계정 복구
- **회원 탈퇴**: 개인정보 완전 삭제

### 2. 반려견 프로필 관리
- **다중 프로필 지원**: 한 사용자가 여러 반려견 등록
- **상세 정보 관리**
  - 기본 정보: 이름, 나이, 견종, 체중
  - 건강 정보: 기저질환, 복용 약물
- **CRUD 기능**: 생성, 조회, 수정, 삭제
- **상담 대상 선택**: 여러 반려견 중 선택하여 상담

### 3. AI 건강 상담
- **맞춤 상담 모드**: 선택한 반려견 프로필 자동 반영
- **빠른 상담 모드**: 프로필 없이 일반 질문
- **대화 히스토리**: 반려견별 상담 내역 저장/조회
- **출처 제공**: 답변 근거가 된 전문 자료 명시
- **실시간 응답**: 스트리밍 방식 답변 생성

---

## 🛠 기술 스택

### Frontend
```
Django 4.2+          - 템플릿 렌더링 및 사용자 인터페이스
HTML5/CSS3/JS        - 반응형 웹 디자인, 커스텀 UI
```

### Backend
```
FastAPI 0.100+       - RESTful API 서버
Pydantic             - 데이터 검증
SQLAlchemy           - ORM
Alembic              - 데이터베이스 마이그레이션
```

### AI/ML
```
LangChain            - RAG 파이프라인 구축
OpenAI GPT-4o-mini   - LLM 모델
BAAI/bge-m3          - 텍스트 임베딩 (HuggingFace)
Chroma               - 벡터 데이터베이스
```

### Database
```
SQLite               - 주 데이터베이스 (개발 환경)
Chroma               - 벡터 DB (수의학 지식)
```

### Authentication
```
JWT (PyJWT)          - 토큰 기반 인증
bcrypt               - 비밀번호 해싱
```

### DevOps
```
Docker               - 컨테이너화
Docker Compose       - 멀티 컨테이너 관리
Nginx                - 리버스 프록시
Gunicorn             - WSGI 서버
```

### Development Tools
```
Git/GitHub           - 버전 관리
Postman              - API 테스트
pytest               - 단위 테스트
```

---

## 🏗 시스템 아키텍처

### 전체 아키텍처 다이어그램

<img width="1376" height="768" alt="최종 아키텍쳐" src="https://github.com/user-attachments/assets/08fefee3-e8d8-4d06-8d21-f53a7da26e1f" />




### 데이터 흐름

```
[사용자 질문 입력]
        ↓
[Django: 프론트엔드 수신]
        ↓
[FastAPI Backend: 사용자 인증 확인 (JWT)]
        ↓
[선택된 반려견 프로필 조회]
        ↓
[FastAPI AI 서빙: RAG 파이프라인 실행]
        ↓
┌───────────────────────────────────────┐
│   질문 + 프로필 → 임베딩 생성          │
│            ↓                          │
│   벡터 DB 유사도 검색 (Top-K)          │
│            ↓                          │
│   관련 문서 조회                       │
│            ↓                          │
│   LLM 프롬프트 구성                    │
│   • 시스템: 수의사 역할                │
│   • 컨텍스트: 검색된 문서              │
│   • 프로필: 반려견 정보                │
│   • 질문: 사용자 입력                  │
│            ↓                          │
│   LLM API 호출 (GPT-4)                │
│            ↓                          │
│   답변 생성 + 출처 첨부                │
└───────────────────────────────────────┘
        ↓
[답변 DB 저장 (ChatHistory)]
        ↓
[Django: 사용자에게 응답 표시]
```

---

## 🗄 ERD 다이어그램

```sql
┌─────────────────────────────────────────────────────────────┐
│                          users                              │
├─────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                              │
│    │ email             VARCHAR     UNIQUE, NOT NULL         │
│    │ username          VARCHAR     UNIQUE, NOT NULL         │
│    │ hashed_password   VARCHAR     NOT NULL                 │
│    │ created_at        DATETIME    DEFAULT CURRENT_TIMESTAMP│
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      dog_profiles                           │
├─────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                              │
│ FK │ owner_id          INTEGER      → users.id              │
│    │ name              VARCHAR      NOT NULL                │
│    │ breed             VARCHAR                              │
│    │ age               INTEGER                              │
│    │ birth_date        VARCHAR                              │
│    │ gender            VARCHAR      (수컷/암컷)             │
│    │ size              VARCHAR      (소형견/중형견/대형견)  │
│    │ weight            VARCHAR                              │
│    │ neutered          VARCHAR      (예/아니오)             │
│    │ health_info       VARCHAR      (기저질환)              │
│    │ medication        VARCHAR      (복용약)                │
│    │ profile_image     VARCHAR      (프로필 이미지 경로)    │
│    │ created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP│
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      chat_messages                          │
├─────────────────────────────────────────────────────────────┤
│ PK │ id                INTEGER                              │
│ FK │ dog_id            INTEGER      → dog_profiles.id (NULL 가능)│
│ FK │ user_id           INTEGER      → users.id (NULL 가능)  │
│    │ session_id        VARCHAR      (세션 그룹화용)         │
│    │ message           TEXT         NOT NULL                │
│    │ is_user           INTEGER      (1: 사용자, 0: AI)      │
│    │ created_at        DATETIME     DEFAULT CURRENT_TIMESTAMP│
│    │                                                         │
│    │ 인덱스:                                                 │
│    │ - ix_chat_user_session (user_id, session_id, created_at)│
│    │ - ix_chat_dog_session (dog_id, session_id, created_at) │
│    │ - ix_chat_session_user_msg (session_id, is_user, created_at)│
└─────────────────────────────────────────────────────────────┘
```

### 관계 설명

**users ↔ dog_profiles (1:N)**
- 한 사용자는 여러 반려견 프로필을 소유할 수 있음
- `CASCADE DELETE`: 사용자 삭제 시 모든 반려견 프로필도 삭제

**dog_profiles ↔ chat_messages (1:N)**
- 한 반려견은 여러 대화 기록을 가짐
- 반려견별로 독립적인 상담 히스토리 관리 (session_id로 그룹화)
- `CASCADE DELETE`: 프로필 삭제 시 관련 대화 기록도 삭제

**users ↔ chat_messages (1:N)**
- 사용자별 전체 대화 기록 추적 가능
- 빠른 상담은 `dog_id = NULL`, `user_id`로만 저장

### 세션 관리
- **session_id**: 대화를 세션 단위로 그룹화
- 같은 session_id를 가진 메시지들이 하나의 대화 세션을 구성
- 사용자는 여러 세션을 가질 수 있으며 각 세션을 독립적으로 조회/삭제 가능

---

## 📊 프로젝트 성과

### 정량적 성과
- ⏱️ **상담 시간 50% 단축**: 반복 입력 제거로 평균 응답 시간 감소
- 🎯 **개인화 정확도**: 프로필 기반 답변으로 사용자 만족도 향상
- 📚 **지식 베이스**: 수의학 서적 10권, 논문 500편, 상담 데이터 1,000건 이상 벡터화
- 🔒 **보안 강화**: JWT + 이메일 인증으로 무단 접근 차단

### 기술적 성과
✅ **3차 → 4차 Iterative 개발**: 사용자 피드백 기반 문제 발견 및 해결  
✅ **확장 가능한 아키텍처**: 프론트엔드-백엔드-AI 서빙 분리로 독립적 확장 가능  
✅ **RAG 시스템 구축**: 검증된 데이터 기반 신뢰성 있는 답변 생성  
✅ **프로필 기반 개인화**: 사용자 경험(UX) 중심 설계

### 차별화 포인트

| 구분 | 일반 검색 엔진 | 기존 AI 챗봇 | **Dr. 멍!** |
|------|--------------|-------------|------------|
| **정보 신뢰성** | ❌ 출처 불명 | ⚠️ 일반적 | ✅ 검증된 수의학 DB |
| **개인화** | ❌ 불가능 | ❌ 불가능 | ✅ 프로필 자동 반영 |
| **맥락 이해** | ❌ 키워드만 | ⚠️ 제한적 | ✅ RAG 기반 맥락 파악 |
| **히스토리 관리** | ❌ 없음 | ⚠️ 세션만 | ✅ 반려견별 저장 |
| **출처 제공** | ❌ 없음 | ❌ 없음 | ✅ 전문 자료 명시 |
| **다중 반려견** | ❌ 불가능 | ❌ 불가능 | ✅ 다중 프로필 지원 |

---

## 📝 회고

### 프로젝트를 통해 배운 점

**1. 사용자 중심 설계의 중요성**
> 3차 프로젝트에서 기술적으로는 성공했지만, 실제 사용 시 "매번 정보 입력"이라는 불편함을 발견했습니다. 이를 통해 **기술의 완성도보다 사용자 경험이 우선**임을 깨달았습니다.

**2. Iterative 개발 프로세스**
> 한 번에 완벽한 제품을 만들려 하지 않고, **작은 문제를 발견하고 해결하는 반복 과정**이 더 나은 결과를 만든다는 것을 경험했습니다.

**3. 아키텍처 설계의 중요성**
> 프론트엔드-백엔드-AI 서빙을 분리한 구조 덕분에 각 레이어를 독립적으로 개선할 수 있었고, 이는 **확장성과 유지보수성**을 크게 향상시켰습니다.

## 🚀 아쉬운 점 및 개선 방향

### 아쉬운 점
**1. 테스트 코드 부족**
- 단위 테스트, 통합 테스트 커버리지 부족
- 향후 pytest 기반 테스트 코드 작성 계획

**2. 성능 최적화**
- RAG 검색 속도 개선 필요 (현재 평균 3-5초)
- 캐싱 전략 도입 검토

**3. 사용자 피드백 시스템**
- 답변 품질 평가 기능 추가 필요
- A/B 테스트 기반 프롬프트 최적화

### 향후 개선 계획

- 📸 **이미지 분석**: 피부 질환, 상처 사진 업로드 및 AI 진단
- 🔔 **알림 시스템**: 예방접종, 약 복용 시간 리마인더
- 🏥 **병원 연계**: 긴급 상황 시 인근 동물병원 예약 연결
- 📱 **모바일 앱**: React Native 기반 크로스 플랫폼 앱
- 🎙️ **음성 인식**: 음성으로 질문하고 답변 듣기

