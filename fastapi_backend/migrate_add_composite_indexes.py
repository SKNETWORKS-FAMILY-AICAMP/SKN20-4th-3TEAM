"""
복합 인덱스 추가 마이그레이션 스크립트
- 채팅 성능을 크게 개선하기 위한 복합 인덱스 추가
"""
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def add_composite_indexes():
    """복합 인덱스 추가"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        try:
            # 1. 빠른상담 세션 조회 최적화 인덱스
            print("빠른상담 세션 조회 인덱스 추가 중...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_chat_user_session
                ON chat_messages(user_id, session_id, created_at)
            """))
            conn.commit()
            print("✅ ix_chat_user_session 인덱스 추가 완료")

            # 2. 강아지 채팅 세션 조회 최적화 인덱스
            print("강아지 채팅 세션 조회 인덱스 추가 중...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_chat_dog_session
                ON chat_messages(dog_id, session_id, created_at)
            """))
            conn.commit()
            print("✅ ix_chat_dog_session 인덱스 추가 완료")

            # 3. 세션의 첫 메시지 조회 최적화 인덱스
            print("첫 메시지 조회 인덱스 추가 중...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_chat_session_user_msg
                ON chat_messages(session_id, is_user, created_at)
            """))
            conn.commit()
            print("✅ ix_chat_session_user_msg 인덱스 추가 완료")

            print("\n🎉 모든 복합 인덱스가 성공적으로 추가되었습니다!")
            print("💡 이제 채팅 세션 조회가 훨씬 빨라집니다.")

        except Exception as e:
            print(f"❌ 인덱스 추가 중 오류 발생: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    add_composite_indexes()
