from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dogs, chat

app = FastAPI(
    title="강아지 채팅 API",
    description="Django 프론트엔드와 연동되는 FastAPI 백엔드",
    version="1.0.0"
)

# CORS 설정 (Django에서 요청할 수 있도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(dogs.router, prefix="/api/dogs", tags=["강아지 프로필"])
app.include_router(chat.router, prefix="/api/chat", tags=["채팅"])


@app.get("/")
def read_root():
    return {
        "message": "강아지 채팅 API 서버",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
