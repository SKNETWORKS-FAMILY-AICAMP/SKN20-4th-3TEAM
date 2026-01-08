from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import ChatMessage, DogProfile
from schemas import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse

router = APIRouter()


@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(chat: ChatMessageCreate, db: Session = Depends(get_db)):
    """채팅 메시지 전송 API
    
    팀원이 구현할 내용:
    1. 사용자 메시지 저장
    2. AI 모델 호출 (GPT, Claude 등)
    3. AI 응답 생성 및 저장
    4. 응답 반환
    """
    # 강아지 프로필 확인
    dog = db.query(DogProfile).filter(DogProfile.id == chat.dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강아지 프로필을 찾을 수 없습니다."
        )
    
    # 사용자 메시지 저장
    user_message = ChatMessage(
        dog_id=chat.dog_id,
        message=chat.message,
        is_user=1
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # TODO: AI 응답 생성 (팀원이 구현)
    # 예: OpenAI API, Anthropic Claude API 등 호출
    ai_response_text = f"안녕하세요! 저는 {dog.name}입니다. 멍멍! (AI 응답 구현 필요)"
    
    # AI 응답 저장
    ai_message = ChatMessage(
        dog_id=chat.dog_id,
        message=ai_response_text,
        is_user=0
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    return ai_message


@router.get("/{dog_id}/history", response_model=List[ChatMessageResponse])
def get_chat_history(dog_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """채팅 히스토리 조회 API
    
    팀원이 구현할 내용:
    1. 특정 강아지와의 대화 내역 조회
    2. 페이지네이션 처리 (선택)
    3. 최신순 정렬
    """
    # 강아지 프로필 확인
    dog = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강아지 프로필을 찾을 수 없습니다."
        )
    
    # 채팅 히스토리 조회
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.dog_id == dog_id)\
        .order_by(ChatMessage.created_at.desc())\
        .limit(limit)\
        .all()
    
    # 시간순으로 정렬 (최신이 마지막)
    messages.reverse()
    
    return messages


@router.delete("/{dog_id}/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_history(dog_id: int, db: Session = Depends(get_db)):
    """채팅 히스토리 삭제 API
    
    팀원이 구현할 내용:
    1. 특정 강아지와의 모든 대화 삭제
    2. 권한 확인
    """
    # 강아지 프로필 확인
    dog = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강아지 프로필을 찾을 수 없습니다."
        )
    
    # 메시지 삭제
    db.query(ChatMessage).filter(ChatMessage.dog_id == dog_id).delete()
    db.commit()
    
    return None
