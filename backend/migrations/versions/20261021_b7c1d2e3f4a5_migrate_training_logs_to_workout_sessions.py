"""migrate training_logs to workout_sessions and drop old table

旧表 training_logs 的语义是「一天一条 + 动作用 JSON 存」，无法支撑
渐进超负荷/容量/PR 分析，已由 workout_sessions + workout_sets 取代。
本迁移负责把历史数据搬过去，再删掉旧表。

Revision ID: b7c1d2e3f4a5
Revises: 59afb5700af1
Create Date: 2026-10-21 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b7c1d2e3f4a5'
down_revision: Union[str, Sequence[str], None] = '59afb5700af1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    has_old = conn.execute(sa.text("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = 'training_logs'
    """)).scalar()

    if has_old:
        # 只搬「这条旧记录在那天还没有新会话」的数据，避免重复导入
        conn.execute(sa.text("""
            INSERT INTO workout_sessions
                (user_id, session_date, title, focus, plan_id, note,
                 duration_min, feeling, total_sets, total_reps, total_volume,
                 created_at, updated_at)
            SELECT t.user_id,
                   t.log_date,
                   LEFT(COALESCE(NULLIF(t.focus, ''), '训练打卡'), 64),
                   LEFT(COALESCE(t.focus, ''), 32),
                   NULLIF(t.plan_id, 0),
                   t.note,
                   0, NULL, 0, 0, 0,
                   t.created_at,
                   t.updated_at
            FROM training_logs t
            WHERE NOT EXISTS (
                SELECT 1 FROM workout_sessions s
                WHERE s.user_id = t.user_id AND s.session_date = t.log_date
            )
        """))
        op.drop_table('training_logs')


def downgrade() -> None:
    op.create_table(
        'training_logs',
        sa.Column('user_id', sa.Integer(), nullable=False, comment='用户 ID'),
        sa.Column('plan_id', sa.Integer(), nullable=False, comment='计划 ID'),
        sa.Column('is_official', sa.Boolean(), nullable=True, comment='是否官方计划'),
        sa.Column('log_date', sa.Date(), nullable=False, comment='训练日期'),
        sa.Column('focus', sa.String(length=32), nullable=True, comment='训练重点'),
        sa.Column('exercises', sa.JSON(), nullable=True, comment='完成动作列表'),
        sa.Column('note', sa.Text(), nullable=True, comment='备注'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='训练打卡（已废弃，仅用于回滚）',
    )

    # 回滚时把每个会话还原成一条旧格式打卡记录（组明细无法还原，属于有损回滚）
    op.get_bind().execute(sa.text("""
        INSERT INTO training_logs
            (user_id, plan_id, is_official, log_date, focus, exercises, note, created_at, updated_at)
        SELECT user_id,
               COALESCE(plan_id, 0),
               0,
               session_date,
               focus,
               JSON_ARRAY(),
               note,
               created_at,
               updated_at
        FROM workout_sessions
    """))
