# -*- coding: utf-8 -*-
"""教练认证与教练档案

流程：用户提交 coach_applications（含身份证正反面 + 资质凭证，存私有目录）→
管理员审核 → 通过后创建 coach_profiles 并置 users.is_coach = True。
证件文件不进 /static（静态目录任何人拿到 URL 就能看），必须走受保护接口读取。
"""
from . import db, BaseModel


class CoachApplication(db.Model, BaseModel):
    __tablename__ = "coach_applications"

    user_id = db.Column(db.Integer, nullable=False, index=True, comment="申请人用户 ID")
    real_name = db.Column(db.String(64), nullable=False, comment="真实姓名")
    phone = db.Column(db.String(20), nullable=False, comment="联系电话")
    id_card_front = db.Column(db.String(256), nullable=False, comment="身份证人像面（私有存储相对路径）")
    id_card_back = db.Column(db.String(256), nullable=False, comment="身份证国徽面（私有存储相对路径）")
    cert_type = db.Column(db.String(32), nullable=False, comment="资质类型：national/ace/nssa/other")
    cert_file = db.Column(db.String(256), nullable=False, comment="资质凭证（私有存储相对路径）")
    bio = db.Column(db.String(500), comment="个人简介")
    specialties = db.Column(db.String(256), comment="专长标签，逗号分隔")
    status = db.Column(db.String(16), default="pending", nullable=False, index=True,
                       comment="pending/approved/rejected")
    reject_reason = db.Column(db.String(256), comment="驳回原因")
    reviewer_id = db.Column(db.Integer, comment="审核人用户 ID")
    reviewed_at = db.Column(db.DateTime, comment="审核时间")

    def to_dict(self, exclude=None, mask=True):
        d = super().to_dict(exclude=exclude)
        # 证件路径不直接下发（前端通过受保护接口取图），证件号没有存库所以无需脱敏
        if mask:
            for k in ("id_card_front", "id_card_back", "cert_file"):
                d[k] = bool(d.get(k))
        return d


class CoachProfile(db.Model, BaseModel):
    __tablename__ = "coach_profiles"

    user_id = db.Column(db.Integer, nullable=False, index=True, comment="教练用户 ID")
    display_name = db.Column(db.String(64), nullable=False, comment="对外展示名")
    bio = db.Column(db.String(500), comment="个人简介")
    specialties = db.Column(db.String(256), comment="专长标签，逗号分隔")
    years = db.Column(db.Integer, default=0, comment="执教年限")
    avatar_url = db.Column(db.String(256), comment="头像（公开静态目录）")
    cert_type = db.Column(db.String(32), comment="资质类型（来自申请）")
    status = db.Column(db.String(16), default="active", comment="active/paused")

    __table_args__ = (
        db.UniqueConstraint("user_id", name="uq_coach_profiles_user_id"),
    )


class CoachStudent(db.Model, BaseModel):
    """教练-学员绑定关系。

    学员主动申请（附留言），教练接受后进入 active；学员申请即视为
    同意教练查看自己的训练数据概览（仅概览统计，不含身体隐私数据）。
    """
    __tablename__ = "coach_students"

    coach_user_id = db.Column(db.Integer, nullable=False, index=True, comment="教练用户 ID")
    student_user_id = db.Column(db.Integer, nullable=False, index=True, comment="学员用户 ID")
    message = db.Column(db.String(256), comment="申请留言")
    status = db.Column(db.String(16), default="pending", nullable=False, index=True,
                       server_default="pending", comment="pending/active/terminated")
    reject_reason = db.Column(db.String(256), comment="教练拒绝原因")
    responded_at = db.Column(db.DateTime, comment="教练处理时间")

    __table_args__ = (
        db.UniqueConstraint("coach_user_id", "student_user_id", name="uq_coach_student_pair"),
    )

    def to_dict(self, exclude=None, with_users=False):
        d = super().to_dict(exclude=exclude)
        if with_users:
            from models.auth import User
            coach = db.session.get(User, self.coach_user_id)
            student = db.session.get(User, self.student_user_id)
            d["coach"] = {
                "id": coach.id, "nickname": coach.nickname, "avatar_url": coach.avatar_url,
            } if coach else None
            d["student"] = {
                "id": student.id, "nickname": student.nickname, "avatar_url": student.avatar_url,
            } if student else None
        return d


class CoachMessage(db.Model, BaseModel):
    """教练-学员站内咨询留言（仅 active 关系内可互发）"""
    __tablename__ = "coach_messages"

    coach_user_id = db.Column(db.Integer, nullable=False, index=True, comment="教练用户 ID")
    student_user_id = db.Column(db.Integer, nullable=False, index=True, comment="学员用户 ID")
    sender_id = db.Column(db.Integer, nullable=False, comment="发送者用户 ID（教练或学员）")
    content = db.Column(db.String(1000), nullable=False, comment="消息内容")
    read_at = db.Column(db.DateTime, comment="对方阅读时间")

    __table_args__ = (
        db.Index("ix_coach_messages_pair_id", "coach_user_id", "student_user_id", "id"),
    )
