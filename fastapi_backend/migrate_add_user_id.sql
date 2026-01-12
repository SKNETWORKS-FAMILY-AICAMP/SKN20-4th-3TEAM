-- ChatMessage 테이블에 user_id 컬럼 추가
-- 빠른채팅을 유저별로 분리하기 위한 마이그레이션

-- user_id 컬럼 추가 (nullable, indexed)
ALTER TABLE chat_messages ADD COLUMN user_id INTEGER;

-- 인덱스 생성 (쿼리 성능 향상)
CREATE INDEX IF NOT EXISTS ix_chat_messages_user_id ON chat_messages (user_id);

-- 기존 데이터에 대한 처리 안내:
-- 기존 빠른채팅 메시지(dog_id가 NULL인 메시지)는 user_id도 NULL로 남아있습니다.
-- 새로운 빠른채팅부터 user_id가 정상적으로 저장됩니다.
-- 필요시 기존 데이터를 수동으로 삭제하거나, 특정 사용자에게 할당할 수 있습니다.
