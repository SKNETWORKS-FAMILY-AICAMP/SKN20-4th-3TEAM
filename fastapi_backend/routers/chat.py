from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import get_db
from models import ChatMessage, DogProfile, User
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# JWT 설정
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """JWT 토큰에서 현재 사용자 정보 추출"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 없습니다."
        )
    
    try:
        # "Bearer <token>" 형식에서 토큰 추출
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 형식입니다."
            )
        
        token = authorization[7:]  # "Bearer " 제거
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 유효하지 않습니다."
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다."
        )
    
    return {"email": email}


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


@router.post("/{dog_id}", response_model=ChatResponse)
def send_message(
    dog_id: int, # URL 경로에서 강아지 ID
    chat_request: ChatRequest, # 요청 본문 (사용자 메시지)
    db: Session = Depends(get_db), # DB 세션 주입
    current_user: dict = Depends(get_current_user) # 인증된 사용자 정보
):
    """현재 사용자의 강아지와 채팅 메시지 전송"""
    email = current_user["email"] # 토큰에서 추출한 이메일
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first() #DB에서 이메일 조회
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 해당 강아지가 현재 사용자의 것인지 확인
    dog = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == user.id
    ).first()
    

    if not dog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 강아지와는 채팅할 수 없습니다."
        )
    
    # 강아지 정보 가져오기
    dog_profile = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    # 메시지 저장
    new_message = ChatMessage(
        dog_id=dog_id,
        message=chat_request.message,
        is_user=True
    )
    db.add(new_message)
    db.commit()
    
    
    # AI 응답 생성 (임시 - 팀원이 AI 모델 연동)
    ai_response = f"안녕하세요! '{chat_request.message}'에 대한 답변입니다. (AI 응답 구현 필요)"
    
    # AI 응답 저장
    ai_message = ChatMessage(
        dog_id=dog_id,
        message=ai_response,
        is_user=False
    )
    db.add(ai_message)
    db.commit()
    
    return {"response": ai_response}


@router.post("/quick", response_model=ChatResponse)
def quick_chat(chat_request: ChatRequest, db: Session = Depends(get_db)):
    """빠른상담 메시지 전송"""
    # 메시지 저장 (dog_profile_id 없이)
    new_message = ChatMessage(
        dog_profile_id=None,  # 빠른상담은 프로필 없음
        message=chat_request.message,
        is_user=True
    )
    db.add(new_message)
    db.commit()
    
    # AI 응답 생성 (임시 - 팀원이 AI 모델 연동)
    ai_response = f"빠른상담: '{chat_request.message}'에 대한 일반적인 답변입니다. (AI 응답 구현 필요)"
    
    # AI 응답 저장
    ai_message = ChatMessage(
        dog_profile_id=None,
        message=ai_response,
        is_user=False
    )
    db.add(ai_message)
    db.commit()
    
    return {"response": ai_response}


@router.get("/{dog_id}/history")
def get_chat_history(
    dog_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """현재 사용자의 강아지 채팅 히스토리 조회"""
    email = current_user["email"]
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 해당 강아지가 현재 사용자의 것인지 확인
    dog = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == user.id
    ).first()
    
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 강아지와는 채팅할 수 없습니다."
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.dog_id == dog_id
    ).order_by(ChatMessage.created_at).all()
    
    return {"messages": messages}