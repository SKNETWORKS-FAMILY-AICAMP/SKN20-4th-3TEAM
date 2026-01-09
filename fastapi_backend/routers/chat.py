from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import ChatMessage, DogProfile, User
from pydantic import BaseModel
from typing import List
from auth_utils import get_current_user
from src.pipeline import run_rag  # 팀원이 구현한 RAG 파이프라인 함수 임포트

router = APIRouter()


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


def build_dog_context(dog) -> str:
    """
    LLM에 넣을 '짧고 구조화된' 강아지 프로필을 만든다.
    (dog: DogProfile 객체)
    """

    disease = getattr(dog, "disease", None) # 없으면 None
    medication = getattr(dog, "medication", None)
    weight = getattr(dog, "weight", None)
    gender = getattr(dog, "gender", None)
    neutered = getattr(dog, "neutered", None)

    parts = [
        f"- 이름: {dog.name}",
        f"- 나이: {dog.age}세",
        f"- 종: {dog.breed}",
    ]
    if weight is not None:
        parts.append(f"- 체중: {weight}kg")
    if gender is not None:
        parts.append(f"- 성별: {gender}")
    if neutered is not None:
        parts.append(f"- 중성화 여부: {neutered}")
    if disease:
        parts.append(f"- 기저질환: {disease}")
    if medication:
        parts.append(f"- 복용약: {medication}")

    return "강아지 프로필\n" + "\n".join(parts)

@router.post("/quick", response_model=ChatResponse)
def quick_chat(chat_request: ChatRequest, db: Session = Depends(get_db)):
    """빠른상담 메시지 전송"""
    # AI 응답 생성 (빠른상담은 강아지 정보 없이)
    try:
        ai_response = run_rag(chat_request.message)
    except Exception as e:
        print(f"RAG 파이프라인 실행 중 오류 발생: {e}")
        ai_response = "죄송합니다. 현재 답변을 생성할 수 없습니다. 잠시 후 다시 시도하세요."
    
    # 메시지와 AI 응답을 한 번에 저장 (성능 최적화)
    new_message = ChatMessage(
        dog_id=None,  # 빠른상담은 프로필 없음
        message=chat_request.message,
        is_user=True
    )
    ai_message = ChatMessage(
        dog_id=None,
        message=ai_response,
        is_user=False
    )
    
    db.add(new_message)
    db.add(ai_message)
    db.commit()  # 1번만 commit
    
    return {"response": ai_response}

@router.post("/{dog_id}", response_model=ChatResponse)
def send_message(
    dog_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지와 채팅 메시지 전송"""

    # DB에서 현재 사용자가 선택한 강아지 정보 조회
    dog = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == current_user.id
    ).first()
    
    # 검증을 먼저 수행
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 강아지와는 채팅할 수 없습니다."
        )

    # 강아지 프로필 정보 생성
    dog_content = build_dog_context(dog)
    


    # RAG 파이프라인 실행 - 응답 생성
    try: 
        ai_response = run_rag(chat_request.message, dog_content) #사용자의 질문과 강아지 프로필을 함께 rag에 전달

    except Exception as e:
        print(f"RAG 파이프라인 실행 중 오류 발생: {e}")
        ai_response = "죄송합니다. 현재 답변을 생성할 수 없습니다. 잠시 후 다시 시도하세요."
    


    # 사용자 질문과 AI 응답을 한 번에 저장 (성능 최적화)
    new_message = ChatMessage(
        dog_id=dog_id,
        message=chat_request.message,
        is_user=True
    )
    ai_message = ChatMessage(
        dog_id=dog_id,
        message=ai_response,
        is_user=False
    )
    
    db.add(new_message)
    db.add(ai_message)
    db.commit()  # 1번만 commit (DB I/O 50% 감소)
    
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