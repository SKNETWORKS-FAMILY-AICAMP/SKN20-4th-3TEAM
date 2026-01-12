"""
FastAPI JWT 인증 관련 공통 유틸리티
"""
from fastapi import Header, HTTPException, status, Depends
from jose import JWTError, jwt
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from models import User

# JWT 설정 (Django settings와 동일하게 관리해야 함)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"


def get_current_user_email(authorization: Optional[str] = Header(None)) -> str:
    """
    Authorization 헤더에서 JWT 토큰을 추출하여 사용자 이메일 반환
    
    Usage: get_current_user_email: str = Depends(get_current_user_email)
    """
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
        
        return email
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유효하지 않습니다."
        )


def get_current_user(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT 토큰에서 추출한 이메일로 사용자 조회
    
    Usage: current_user: User = Depends(get_current_user)
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    return user

