"""create coach tables and users.is_coach

教练认证功能：新增 coach_applications（申请与审核记录）、coach_profiles
（认证通过后的教练档案），users 增加 is_coach 标记。

Revision ID: c8f2a6d9e1b4
Revises: b7c1d2e3f4a5
Create Date: 2026-10-26 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c8f2a6d9e1b4'
down_revision: Union[str, Sequence[str], None] = 'b7c1d2e3f4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_coach', sa.Boolean(), nullable=False,
                                     comment='是否认证教练'))
    op.create_index(op.f('ix_users_is_coach'), 'users', ['is_coach'], unique=False)

    op.create_table('coach_applications',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='申请人用户 ID'),
    sa.Column('real_name', sa.String(length=64), nullable=False, comment='真实姓名'),
    sa.Column('phone', sa.String(length=20), nullable=False, comment='联系电话'),
    sa.Column('id_card_front', sa.String(length=256), nullable=False, comment='身份证人像面（私有存储相对路径）'),
    sa.Column('id_card_back', sa.String(length=256), nullable=False, comment='身份证国徽面（私有存储相对路径）'),
    sa.Column('cert_type', sa.String(length=32), nullable=False, comment='资质类型：national/ace/nssa/other'),
    sa.Column('cert_file', sa.String(length=256), nullable=False, comment='资质凭证（私有存储相对路径）'),
    sa.Column('bio', sa.String(length=500), nullable=True, comment='个人简介'),
    sa.Column('specialties', sa.String(length=256), nullable=True, comment='专长标签，逗号分隔'),
    sa.Column('status', sa.String(length=16), nullable=False, comment='pending/approved/rejected'),
    sa.Column('reject_reason', sa.String(length=256), nullable=True, comment='驳回原因'),
    sa.Column('reviewer_id', sa.Integer(), nullable=True, comment='审核人用户 ID'),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True, comment='审核时间'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coach_applications_user_id'), 'coach_applications', ['user_id'], unique=False)
    op.create_index(op.f('ix_coach_applications_status'), 'coach_applications', ['status'], unique=False)

    op.create_table('coach_profiles',
    sa.Column('user_id', sa.Integer(), nullable=False, comment='教练用户 ID'),
    sa.Column('display_name', sa.String(length=64), nullable=False, comment='对外展示名'),
    sa.Column('bio', sa.String(length=500), nullable=True, comment='个人简介'),
    sa.Column('specialties', sa.String(length=256), nullable=True, comment='专长标签，逗号分隔'),
    sa.Column('years', sa.Integer(), nullable=True, comment='执教年限'),
    sa.Column('avatar_url', sa.String(length=256), nullable=True, comment='头像（公开静态目录）'),
    sa.Column('cert_type', sa.String(length=32), nullable=True, comment='资质类型（来自申请）'),
    sa.Column('status', sa.String(length=16), nullable=True, comment='active/paused'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', name='uq_coach_profiles_user_id')
    )
    op.create_index(op.f('ix_coach_profiles_user_id'), 'coach_profiles', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_coach_profiles_user_id'), table_name='coach_profiles')
    op.drop_table('coach_profiles')
    op.drop_index(op.f('ix_coach_applications_status'), table_name='coach_applications')
    op.drop_index(op.f('ix_coach_applications_user_id'), table_name='coach_applications')
    op.drop_table('coach_applications')
    op.drop_index(op.f('ix_users_is_coach'), table_name='users')
    op.drop_column('users', 'is_coach')
