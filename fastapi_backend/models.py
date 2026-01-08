from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    dogs = relationship("DogProfile", back_populates="owner")


class DogProfile(Base):
    """강아지 프로필 모델"""
    __tablename__ = "dog_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    breed = Column(String)  # 견종
    age = Column(Integer)
    birth_date = Column(String)  # 생년월일
    gender = Column(String)  # 성별 (수컷/암컷)
    size = Column(String)  # 크기 (소형견/중형견/대형견)
    weight = Column(String)  # 체중
    neutered = Column(String)  # 중성화 여부 (예/아니오)
    health_info = Column(String)  # 기저 질환
    medication = Column(String)  # 복용약
    personality = Column(String)  # 성격 설명
    profile_image = Column(String)  # 프로필 이미지 경로
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    owner = relationship("User", back_populates="dogs")
    chat_messages = relationship("ChatMessage", back_populates="dog")


class ChatMessage(Base):
    """채팅 메시지 모델"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    dog_id = Column(Integer, ForeignKey("dog_profiles.id"))
    message = Column(Text, nullable=False)
    is_user = Column(Integer, default=1)  # 1: 사용자, 0: AI
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    dog = relationship("DogProfile", back_populates="chat_messages")
