"""
데이터베이스 테이블 생성 스크립트
"""
from database import engine, Base
from models import User, DogProfile, ChatMessage

# 모든 테이블 생성
Base.metadata.create_all(bind=engine)

print("✅ 데이터베이스 테이블이 생성되었습니다!")
print("생성된 테이블:")
print("- users")
print("- dog_profiles")
print("- chat_messages")
