from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import ChatMessage, DogProfile, User
from pydantic import BaseModel
from typing import List
from auth_utils import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


@router.post("/{dog_id}", response_model=ChatResponse)
def send_message(
    dog_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지와 채팅 메시지 전송"""
    # 해당 강아지가 현재 사용자의 것인지 확인
    dog = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == current_user.id
    ).first()
    
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 강아지와는 채팅할 수 없습니다."
        )
    
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 채팅 히스토리 조회"""
    # 해당 강아지가 현재 사용자의 것인지 확인
    dog = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == current_user.id
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