from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import DogProfile, User
from schemas import DogProfileCreate, DogProfileResponse
from typing import List
from auth_utils import get_current_user

router = APIRouter()


@router.get("/", response_model=List[DogProfileResponse])
def get_dog_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 프로필 조회"""
    # 해당 사용자의 강아지 프로필만 조회
    profiles = db.query(DogProfile).filter(DogProfile.owner_id == current_user.id).all()
    return profiles


@router.post("/", response_model=DogProfileResponse, status_code=status.HTTP_201_CREATED)
def create_dog_profile(
    profile: DogProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자를 위한 강아지 프로필 생성"""
    # 사용자에게 소속된 새 강아지 프로필 생성
    new_profile = DogProfile(
        name=profile.name,
        breed=profile.breed,
        age=profile.age,
        birth_date=profile.birth_date,
        gender=profile.gender,
        size=profile.size,
        weight=profile.weight,
        neutered=profile.neutered,
        health_info=profile.health_info,
        medication=profile.medication,
        personality=profile.personality,
        owner_id=current_user.id  # 현재 사용자의 ID 설정
    )
    
    db.add(new_profile)
    db.commit()
    # refresh() 제거 - 불필요한 DB 재조회 방지
    
    return new_profile


@router.get("/{dog_id}", response_model=DogProfileResponse)
def get_dog_profile(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 특정 강아지 프로필 조회"""
    # 해당 강아지가 현재 사용자의 것인지 확인
    profile = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == current_user.id
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 프로필 수정"""
    # 해당 강아지가 현재 사용자의 것인지 확인
    existing_profile = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == current_user.id
    ).first()
    
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    # 업데이트
    existing_profile.name = profile.name
    existing_profile.breed = profile.breed
    existing_profile.age = profile.age
    existing_profile.birth_date = profile.birth_date
    existing_profile.gender = profile.gender
    existing_profile.size = profile.size
    existing_profile.weight = profile.weight
    existing_profile.neutered = profile.neutered
    existing_profile.health_info = profile.health_info
    existing_profile.medication = profile.medication
    existing_profile.personality = profile.personality
    
    db.commit()
    db.refresh(existing_profile)
    
    return existing_profile


@router.delete("/{dog_id}")
def delete_dog_profile(
    dog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """현재 사용자의 강아지 프로필 삭제"""
    # 해당 강아지가 현재 사용자의 것인지 확인
    profile = db.query(DogProfile).filter(
        DogProfile.id == dog_id,
        DogProfile.owner_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    db.delete(profile)
    db.commit()
    
    return {"message": "프로필이 삭제되었습니다."}

