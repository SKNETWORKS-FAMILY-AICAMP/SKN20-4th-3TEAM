from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserResponse, Token
from pydantic import BaseModel
import hashlib

router = APIRouter()

# JWT 설정 (auth_utils.py와 동일해야 함)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 1일


def hash_password(password: str):
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str):
    """비밀번호 확인"""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 스키마
class PasswordResetRequest(BaseModel):
    email: str
    new_password: str


class PasswordChangeRequest(BaseModel):
    email: str
    current_password: str
    new_password: str


class ProfileUpdateRequest(BaseModel):
    email: str
    username: str


@router.get("/check-email/{email}")
def check_email_exists(email: str, db: Session = Depends(get_db)):
    """이메일 중복 체크 API"""
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        return {"exists": True, "message": "이미 가입된 이메일 주소입니다."}
    else:
        return {"exists": False, "message": "사용 가능한 이메일입니다."}


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """회원가입 API"""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다."
        )
    
    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """로그인 API"""
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다."
        )
    
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다."
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id
    }


@router.post("/reset-password")
def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """비밀번호 재설정 API (로그인 전 - 이메일 인증 완료 후)"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "비밀번호가 재설정되었습니다."}


@router.post("/change-password")
def change_password(request: PasswordChangeRequest, db: Session = Depends(get_db)):
    """비밀번호 변경 API (로그인 후)"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다."
        )
    
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "비밀번호가 변경되었습니다."}


@router.post("/update-profile")
def update_profile(request: ProfileUpdateRequest, db: Session = Depends(get_db)):
    """프로필 업데이트 API (닉네임 변경)"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 닉네임 중복 체크 (자기 자신 제외)
    existing_username = db.query(User).filter(
        User.username == request.username,
        User.email != request.email
    ).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 닉네임입니다."
        )
    
    user.username = request.username
    db.commit()
    db.refresh(user)
    
    return {"message": "프로필이 업데이트되었습니다.", "username": user.username}


@router.get("/user-info/{email}")
def get_user_info(email: str, db: Session = Depends(get_db)):
    """사용자 정보 조회"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return {
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at
    }


@router.delete("/delete-account/{email}")
def delete_account(email: str, db: Session = Depends(get_db)):
    """계정 삭제"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "계정이 삭제되었습니다."}


@router.get("/me", response_model=UserResponse)
def get_current_user():
    """현재 로그인한 사용자 정보 조회"""
    # TODO: 팀원이 JWT 인증 구현
    return {"message": "JWT 인증 구현 필요"}