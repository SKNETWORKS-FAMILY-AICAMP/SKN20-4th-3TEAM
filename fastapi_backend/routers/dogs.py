from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import get_db
from models import DogProfile, User
from schemas import DogProfileCreate, DogProfileResponse
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


@router.get("/", response_model=List[DogProfileResponse])
def get_dog_profiles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """현재 사용자의 강아지 프로필 조회"""
    email = current_user["email"]
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 해당 사용자의 강아지 프로필만 조회
    profiles = db.query(DogProfile).filter(DogProfile.owner_id == user.id).all()
    return profiles


@router.post("/", response_model=DogProfileResponse, status_code=status.HTTP_201_CREATED)
def create_dog_profile(
    profile: DogProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """현재 사용자를 위한 강아지 프로필 생성"""
    email = current_user["email"]
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # ⭐ 1. 프로필 개수 제한 체크 (최대 10개)
    existing_profiles = db.query(DogProfile).filter(DogProfile.owner_id == user.id).all()
    if len(existing_profiles) >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="프로필은 최대 10개까지만 생성할 수 있습니다."
        )
    
    # ⭐ 2. 이름 중복 체크 (같은 사용자 내에서)
    duplicate_name = db.query(DogProfile).filter(
        DogProfile.owner_id == user.id,
        DogProfile.name == profile.name
    ).first()
    
    if duplicate_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{profile.name}' 이름은 이미 사용 중입니다. 다른 이름을 사용해주세요."
        )
    
    # 사용자에게 소속된 새 강아지 프로필 생성
    new_profile = DogProfile(
        name=profile.name,
        breed=profile.breed,
        age=profile.age,
        personality=profile.personality,
        owner_id=user.id  # 현재 사용자의 ID 설정
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile


@router.get("/{dog_id}", response_model=DogProfileResponse)
def get_dog_profile(
    dog_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """현재 사용자의 특정 강아지 프로필 조회"""
    email = current_user["email"]
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 해당 강아지가 현재 사용자의 것인지 확인
    profile = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    return profile


@router.put("/{dog_id}", response_model=DogProfileResponse)
def update_dog_profile(
    dog_id: int,
    profile: DogProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """현재 사용자의 강아지 프로필 수정"""
    email = current_user["email"]
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 해당 강아지가 현재 사용자의 것인지 확인
    existing_profile = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == user.id
    ).first()
    
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    # ⭐ 이름 변경 시 중복 체크 (자기 자신 제외)
    if profile.name != existing_profile.name:
        duplicate_name = db.query(DogProfile).filter(
            DogProfile.owner_id == user.id,
            DogProfile.name == profile.name,
            DogProfile.id != dog_id
        ).first()
        
        if duplicate_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{profile.name}' 이름은 이미 사용 중입니다. 다른 이름을 사용해주세요."
            )
    
    # 업데이트
    existing_profile.name = profile.name
    existing_profile.breed = profile.breed
    existing_profile.age = profile.age
    existing_profile.personality = profile.personality
    
    db.commit()
    db.refresh(existing_profile)
    
    return existing_profile


@router.delete("/{dog_id}")
def delete_dog_profile(
    dog_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """현재 사용자의 강아지 프로필 삭제"""
    email = current_user["email"]
    
    # 사용자 찾기
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 해당 강아지가 현재 사용자의 것인지 확인
    profile = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    db.delete(profile)
    db.commit()
    
    return {"message": "프로필이 삭제되었습니다."}