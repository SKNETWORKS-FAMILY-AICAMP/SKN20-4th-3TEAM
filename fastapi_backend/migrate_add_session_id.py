"""
ChatMessage 테이블에 session_id 컬럼을 추가하는 마이그레이션 스크립트

사용법:
    python migrate_add_session_id.py
"""

import sqlite3
import os
import sys

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# DB 파일 경로
DB_PATH = "dog_chat.db"

def run_migration():
    """마이그레이션 실행"""
    if not os.path.exists(DB_PATH):
        print(f"오류: 데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")
        return False

    try:
        # DB 연결
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 이미 session_id 컬럼이 있는지 확인
        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'session_id' in columns:
            print("✓ session_id 컬럼이 이미 존재합니다. 마이그레이션을 건너뜁니다.")
            conn.close()
            return True

        print("마이그레이션을 시작합니다...")

        # session_id 컬럼 추가
        cursor.execute("ALTER TABLE chat_messages ADD COLUMN session_id TEXT")
        print("✓ session_id 컬럼이 추가되었습니다.")

        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_chat_messages_session_id ON chat_messages (session_id)")
        print("✓ session_id 인덱스가 생성되었습니다.")

        # 커밋
        conn.commit()
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ChatMessage 테이블 마이그레이션 - session_id 추가")
    print("=" * 60)
    print()

    success = run_migration()

    print()
    print("=" * 60)

    if success:
        print("이제 FastAPI 서버를 재시작하면 변경사항이 적용됩니다.")
    else:
        print("마이그레이션에 실패했습니다. 위의 오류 메시지를 확인하세요.")
