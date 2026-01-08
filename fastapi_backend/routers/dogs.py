from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import DogProfile
from schemas import DogProfileCreate, DogProfileResponse

router = APIRouter()


@router.post("/", response_model=DogProfileResponse, status_code=status.HTTP_201_CREATED)
def create_dog_profile(dog: DogProfileCreate, db: Session = Depends(get_db)):
    """강아지 프로필 생성 API
    
    팀원이 구현할 내용:
    1. 현재 로그인한 사용자 확인 (JWT 토큰)
    2. 강아지 프로필 생성
    3. 프로필 이미지 업로드 처리
    """
    # TODO: JWT에서 user_id 가져오기
    user_id = 1  # 임시로 1로 설정
    
    new_dog = DogProfile(
        name=dog.name,
        breed=dog.breed,
        age=dog.age,
        personality=dog.personality,
        owner_id=user_id
    )
    
    db.add(new_dog)
    db.commit()
    db.refresh(new_dog)
    
    return new_dog


@router.get("/", response_model=List[DogProfileResponse])
def get_my_dogs(db: Session = Depends(get_db)):
    """내 강아지 프로필 목록 조회 API
    
    팀원이 구현할 내용:
    1. 현재 로그인한 사용자 확인
    2. 해당 사용자의 강아지 프로필 목록 반환
    """
    # TODO: JWT에서 user_id 가져오기
    user_id = 1  # 임시로 1로 설정
    
    dogs = db.query(DogProfile).filter(DogProfile.owner_id == user_id).all()
    
    return dogs


@router.get("/{dog_id}", response_model=DogProfileResponse)
def get_dog_profile(dog_id: int, db: Session = Depends(get_db)):
    """특정 강아지 프로필 조회 API
    
    팀원이 구현할 내용:
    1. dog_id로 프로필 조회
    2. 해당 프로필이 현재 사용자의 것인지 확인
    """
    dog = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강아지 프로필을 찾을 수 없습니다."
        )
    
    return dog


@router.put("/{dog_id}", response_model=DogProfileResponse)
def update_dog_profile(dog_id: int, dog: DogProfileCreate, db: Session = Depends(get_db)):
    """강아지 프로필 수정 API
    
    팀원이 구현할 내용:
    1. 프로필 존재 여부 확인
    2. 권한 확인 (본인의 프로필인지)
    3. 프로필 정보 업데이트
    """
    existing_dog = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    if not existing_dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강아지 프로필을 찾을 수 없습니다."
        )
    
    existing_dog.name = dog.name
    existing_dog.breed = dog.breed
    existing_dog.age = dog.age
    existing_dog.personality = dog.personality
    
    db.commit()
    db.refresh(existing_dog)
    
    return existing_dog


@router.delete("/{dog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dog_profile(dog_id: int, db: Session = Depends(get_db)):
    """강아지 프로필 삭제 API
    
    팀원이 구현할 내용:
    1. 프로필 존재 여부 확인
    2. 권한 확인
    3. 프로필 삭제
    """
    dog = db.query(DogProfile).filter(DogProfile.id == dog_id).first()
    
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="강아지 프로필을 찾을 수 없습니다."
        )
    
    db.delete(dog)
    db.commit()
    
    return None
