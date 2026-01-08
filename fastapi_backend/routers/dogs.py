from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import DogProfile
from schemas import DogProfileCreate, DogProfileResponse
from typing import List

router = APIRouter()


@router.get("/", response_model=List[DogProfileResponse])
def get_dog_profiles(db: Session = Depends(get_db)):
    """모든 강아지 프로필 조회 (임시 - 실제로는 사용자별로 필터링)"""
    profiles = db.query(DogProfile).all()
    return profiles


@router.post("/", response_model=DogProfileResponse, status_code=status.HTTP_201_CREATED)
def create_dog_profile(profile: DogProfileCreate, db: Session = Depends(get_db)):
    """강아지 프로필 생성"""
    new_profile = DogProfile(
        name=profile.name,
        breed=profile.breed,
        age=profile.age,
        personality=profile.personality
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return new_profile


@router.get("/{dog_id}", response_model=DogProfileResponse)
def get_dog_profile(dog_id: int, db: Session = Depends(get_db)):
    """특정 강아지 프로필 조회"""
    profile = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    return profile


@router.put("/{dog_id}", response_model=DogProfileResponse)
def update_dog_profile(dog_id: int, profile: DogProfileCreate, db: Session = Depends(get_db)):
    """강아지 프로필 수정"""
    existing_profile = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
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
def delete_dog_profile(dog_id: int, db: Session = Depends(get_db)):
    """강아지 프로필 삭제"""
    profile = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필을 찾을 수 없습니다."
        )
    
    db.delete(profile)
    db.commit()
    
    return {"message": "프로필이 삭제되었습니다."}

