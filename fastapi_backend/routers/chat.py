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
    session_id: str = None  # 세션 ID (선택)

class ChatResponse(BaseModel):
    response: str


def build_dog_context(dog) -> str:
    """
    LLM에 넣을 '짧고 구조화된' 강아지 프로필을 만든다.
    (dog: DogProfile 객체)
    """

    disease = getattr(dog, "health_info", None) # 없으면 None
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
def quick_chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """빠른상담 메시지 전송 (유저별 분리)"""
    # AI 응답 생성 (빠른상담은 강아지 정보 없이)
    try:
        ai_response = run_rag(chat_request.message)
    except Exception as e:
        print(f"RAG 파이프라인 실행 중 오류 발생: {e}")
        ai_response = "죄송합니다. 현재 답변을 생성할 수 없습니다. 잠시 후 다시 시도하세요."

    # 메시지와 AI 응답을 한 번에 저장 (성능 최적화)
    new_message = ChatMessage(
        dog_id=None,  # 빠른상담은 프로필 없음
        user_id=current_user.id,  # 유저별 구분
        session_id=chat_request.session_id,  # 세션 ID 저장
        message=chat_request.message,
        is_user=True
    )
    ai_message = ChatMessage(
        dog_id=None,
        user_id=current_user.id,  # 유저별 구분
        session_id=chat_request.session_id,  # 세션 ID 저장
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
        user_id=current_user.id,  # 유저 ID 저장
        session_id=chat_request.session_id,  # 세션 ID 저장
        message=chat_request.message,
        is_user=True
    )
    ai_message = ChatMessage(
        dog_id=dog_id,
        user_id=current_user.id,  # 유저 ID 저장
        session_id=chat_request.session_id,  # 세션 ID 저장
        message=ai_response,
        is_user=False
    )

    db.add(new_message)
    db.add(ai_message)
    db.commit()  # 1번만 commit (DB I/O 50% 감소)

    return {"response": ai_response}




@router.get("/quick/history")
def get_quick_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 빠른상담 히스토리 조회"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.dog_id == None,
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at).all()

    return {"messages": messages}


@router.get("/quick/sessions")
def get_quick_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 빠른상담 세션 목록 조회"""
    from sqlalchemy import func

    # session_id별로 그룹화하여 첫 번째 메시지와 시간 조회
    sessions = db.query(
        ChatMessage.session_id,
        func.min(ChatMessage.created_at).label('created_at'),
        func.count(ChatMessage.id).label('message_count')
    ).filter(
        ChatMessage.dog_id == None,
        ChatMessage.user_id == current_user.id,
        ChatMessage.session_id != None
    ).group_by(ChatMessage.session_id).order_by(func.min(ChatMessage.created_at).desc()).all()

    # 각 세션의 첫 번째 사용자 메시지 조회
    result = []
    for session in sessions:
        first_msg = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.session_id,
            ChatMessage.is_user == 1
        ).order_by(ChatMessage.created_at).first()

        result.append({
            "session_id": session.session_id,
            "title": first_msg.message[:30] + "..." if first_msg and len(first_msg.message) > 30 else (first_msg.message if first_msg else "새 대화"),
            "created_at": session.created_at,
            "message_count": session.message_count
        })

    return {"sessions": result}


@router.get("/quick/sessions/{session_id}/messages")
def get_quick_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 빠른상담 세션의 메시지 조회"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.dog_id == None,
        ChatMessage.user_id == current_user.id,
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    return {"messages": messages}


@router.delete("/quick/sessions/{session_id}")
def delete_quick_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 빠른상담 특정 세션 삭제"""
    deleted_count = db.query(ChatMessage).filter(
        ChatMessage.dog_id == None,
        ChatMessage.user_id == current_user.id,
        ChatMessage.session_id == session_id
    ).delete()

    db.commit()

    return {"success": True, "deleted_count": deleted_count}


@router.delete("/quick/history")
def delete_quick_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 빠른상담 히스토리 전체 삭제"""
    deleted_count = db.query(ChatMessage).filter(
        ChatMessage.dog_id == None,
        ChatMessage.user_id == current_user.id
    ).delete()

    db.commit()

    return {"success": True, "deleted_count": deleted_count}


@router.get("/{dog_id}/sessions")
def get_dog_chat_sessions(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 채팅 세션 목록 조회"""
    from sqlalchemy import func

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

    # session_id별로 그룹화하여 첫 번째 메시지와 시간 조회
    sessions = db.query(
        ChatMessage.session_id,
        func.min(ChatMessage.created_at).label('created_at'),
        func.count(ChatMessage.id).label('message_count')
    ).filter(
        ChatMessage.dog_id == dog_id,
        ChatMessage.session_id != None
    ).group_by(ChatMessage.session_id).order_by(func.min(ChatMessage.created_at).desc()).all()

    # 각 세션의 첫 번째 사용자 메시지 조회
    result = []
    for session in sessions:
        first_msg = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.session_id,
            ChatMessage.is_user == 1
        ).order_by(ChatMessage.created_at).first()

        result.append({
            "session_id": session.session_id,
            "title": first_msg.message[:30] + "..." if first_msg and len(first_msg.message) > 30 else (first_msg.message if first_msg else "새 대화"),
            "created_at": session.created_at,
            "message_count": session.message_count
        })

    return {"sessions": result}


@router.get("/{dog_id}/sessions/{session_id}/messages")
def get_dog_session_messages(
    dog_id: int,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 강아지 채팅 세션의 메시지 조회"""
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
        ChatMessage.dog_id == dog_id,
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    return {"messages": messages}


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


@router.delete("/{dog_id}/sessions/{session_id}")
def delete_dog_chat_session(
    dog_id: int,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 채팅 특정 세션 삭제"""
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

    deleted_count = db.query(ChatMessage).filter(
        ChatMessage.dog_id == dog_id,
        ChatMessage.session_id == session_id
    ).delete()

    db.commit()

    return {"success": True, "deleted_count": deleted_count}


@router.delete("/{dog_id}/history")
def delete_chat_history(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 채팅 히스토리 전체 삭제"""
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

    deleted_count = db.query(ChatMessage).filter(
        ChatMessage.dog_id == dog_id
    ).delete()

    db.commit()

    return {"success": True, "deleted_count": deleted_count}