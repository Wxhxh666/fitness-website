"""coach students binding and messages

M3 学员体系：新增 coach_students（教练-学员绑定关系，唯一约束
coach+student，状态 pending/active/terminated）与 coach_messages
（站内咨询留言，仅 active 关系内互发）。

Revision ID: d9a3b7c5e2f6
Revises: c8f2a6d9e1b4
Create Date: 2026-10-26 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd9a3b7c5e2f6'
down_revision: Union[str, Sequence[str], None] = 'c8f2a6d9e1b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('coach_students',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('coach_user_id', sa.Integer(), nullable=False, comment='教练用户 ID'),
    sa.Column('student_user_id', sa.Integer(), nullable=False, comment='学员用户 ID'),
    sa.Column('message', sa.String(length=256), comment='申请留言'),
    sa.Column('status', sa.String(length=16), nullable=False,
              server_default='pending', comment='pending/active/terminated'),
    sa.Column('reject_reason', sa.String(length=256), comment='教练拒绝原因'),
    sa.Column('responded_at', sa.DateTime(), comment='教练处理时间'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('coach_user_id', 'student_user_id', name='uq_coach_student_pair'),
    )
    op.create_index(op.f('ix_coach_students_coach_user_id'),
                    'coach_students', ['coach_user_id'], unique=False)
    op.create_index(op.f('ix_coach_students_student_user_id'),
                    'coach_students', ['student_user_id'], unique=False)
    op.create_index(op.f('ix_coach_students_status'),
                    'coach_students', ['status'], unique=False)

    op.create_table('coach_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('coach_user_id', sa.Integer(), nullable=False, comment='教练用户 ID'),
    sa.Column('student_user_id', sa.Integer(), nullable=False, comment='学员用户 ID'),
    sa.Column('sender_id', sa.Integer(), nullable=False,
              comment='发送者用户 ID（教练或学员）'),
    sa.Column('content', sa.String(length=1000), nullable=False, comment='消息内容'),
    sa.Column('read_at', sa.DateTime(), comment='对方阅读时间'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_coach_messages_coach_user_id'),
                    'coach_messages', ['coach_user_id'], unique=False)
    op.create_index(op.f('ix_coach_messages_student_user_id'),
                    'coach_messages', ['student_user_id'], unique=False)
    op.create_index('ix_coach_messages_pair_id', 'coach_messages',
                    ['coach_user_id', 'student_user_id', 'id'], unique=False)


def downgrade() -> None:
    op.drop_table('coach_messages')
    op.drop_table('coach_students')
