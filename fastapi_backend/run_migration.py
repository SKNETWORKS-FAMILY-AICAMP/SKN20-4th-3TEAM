"""
ChatMessage 테이블에 user_id 컬럼을 추가하는 마이그레이션 스크립트

사용법:
    python run_migration.py
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

        # 이미 user_id 컬럼이 있는지 확인
        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'user_id' in columns:
            print("✓ user_id 컬럼이 이미 존재합니다. 마이그레이션을 건너뜁니다.")
            conn.close()
            return True

        print("마이그레이션을 시작합니다...")

        # user_id 컬럼 추가
        cursor.execute("ALTER TABLE chat_messages ADD COLUMN user_id INTEGER")
        print("✓ user_id 컬럼이 추가되었습니다.")

        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_chat_messages_user_id ON chat_messages (user_id)")
        print("✓ user_id 인덱스가 생성되었습니다.")

        # 커밋
        conn.commit()
        print("\n✅ 마이그레이션이 성공적으로 완료되었습니다!")

        # 통계 출력
        cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE dog_id IS NULL AND user_id IS NULL")
        orphan_count = cursor.fetchone()[0]

        if orphan_count > 0:
            print(f"\n⚠️  참고: user_id가 NULL인 기존 빠른채팅 메시지 {orphan_count}개가 있습니다.")
            print("   이 메시지들은 어떤 사용자에게도 표시되지 않습니다.")
            print("   필요시 수동으로 삭제하거나 특정 사용자에게 할당할 수 있습니다.")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ChatMessage 테이블 마이그레이션")
    print("=" * 60)
    print()

    success = run_migration()

    print()
    print("=" * 60)

    if success:
        print("이제 FastAPI 서버를 재시작하면 변경사항이 적용됩니다.")
    else:
        print("마이그레이션에 실패했습니다. 위의 오류 메시지를 확인하세요.")
