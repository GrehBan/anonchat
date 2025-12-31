from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'add_virtual_sequencing'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('messages', 
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_chat_created_active 
        ON messages(chat_id, created_at) 
        WHERE deleted_at IS NULL
    """)
    
    op.execute("DROP VIEW IF EXISTS messages_ordered")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS messages_ordered")
    
    op.execute("""
        CREATE VIEW messages_ordered AS
        SELECT 
            m.message_id,
            m.chat_id,
            m.sender_id,
            m.sequence AS original_sequence,
            -- Вычисляем номер строки на лету
            ROW_NUMBER() OVER (
                PARTITION BY m.chat_id 
                ORDER BY m.created_at ASC
            ) - 1 AS virtual_sequence,
            m.content_text,
            m.content_media,
            m.created_at,
            m.deleted_at
        FROM messages m
        WHERE m.deleted_at IS NULL
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS messages_ordered")
    op.drop_index('idx_messages_chat_created_active', table_name='messages')
    op.drop_column('messages', 'deleted_at')