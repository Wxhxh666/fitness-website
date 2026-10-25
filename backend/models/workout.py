# -*- coding: utf-8 -*-
"""
运动记录模型（细化到「组」）。

旧版用 training_logs 一张表存「一天一条 + JSON 动作列表」，导致三件事做不了：
渐进超负荷分析、训练容量统计、PR 追踪。这里拆成三张表：

  workout_sessions  一次训练（一次进健身房）
    └── workout_sets  一组（动作 + 重量 + 次数 + RPE）
  personal_records    个人纪录（按动作 + 纪录类型唯一）

设计取舍：
- workout_sets 冗余存 exercise_name 和 user_id：
  * 动作库里的动作可能被管理员改名/删除，历史记录必须保留当时的名字；
  * 按用户查历史曲线时不必 join sessions，少一次关联。
- session 上的 total_sets / total_reps / total_volume 是**冗余汇总字段**，
  每次增删改组后由 service 重算。列表页/统计页只读这一列，避免每次 SUM 全表。
"""
from datetime import date, datetime

from . import db, BaseModel

# 纪录类型
PR_E1RM = "e1rm"            # 估算 1RM（Epley 公式）
PR_MAX_WEIGHT = "max_weight"  # 单组最大重量
PR_MAX_REPS = "max_reps"      # 单组最多次数
PR_MAX_VOLUME = "max_volume"  # 单组最大容量（重量 × 次数）


class WorkoutSession(db.Model, BaseModel):
    __tablename__ = "workout_sessions"
    __table_args__ = (
        db.Index("ix_workout_sessions_user_date", "user_id", "session_date"),
    )

    user_id = db.Column(db.Integer, nullable=False, index=True, comment="用户 ID")
    session_date = db.Column(db.Date, nullable=False, comment="训练日期")
    title = db.Column(db.String(64), default="", comment="训练标题，如 胸部训练")
    focus = db.Column(db.String(32), default="", comment="训练部位/重点")
    plan_id = db.Column(db.Integer, default=None, comment="关联的计划 ID（可空）")
    note = db.Column(db.Text, comment="备注")
    duration_min = db.Column(db.Integer, default=0, comment="训练时长（分钟）")
    feeling = db.Column(db.Integer, default=None, comment="主观感受 1-5")

    # 冗余汇总，增删改组后重算
    total_sets = db.Column(db.Integer, default=0, comment="总组数")
    total_reps = db.Column(db.Integer, default=0, comment="总次数")
    total_volume = db.Column(db.Float, default=0.0, comment="总容量 kg（重量×次数）")

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        if isinstance(d.get("session_date"), date):
            d["session_date"] = d["session_date"].isoformat()
        return d


class WorkoutSet(db.Model, BaseModel):
    __tablename__ = "workout_sets"
    __table_args__ = (
        db.Index("ix_workout_sets_session", "session_id", "exercise_name"),
        db.Index("ix_workout_sets_user_exercise", "user_id", "exercise_name"),
    )

    session_id = db.Column(db.Integer, nullable=False, comment="所属训练 ID")
    user_id = db.Column(db.Integer, nullable=False, comment="用户 ID（冗余，便于按用户查动作历史）")
    exercise_id = db.Column(db.Integer, default=None, comment="动作库 ID（可空，自建动作无 ID）")
    exercise_name = db.Column(db.String(64), nullable=False, comment="动作名快照")
    set_index = db.Column(db.Integer, default=1, comment="第几组")
    weight_kg = db.Column(db.Float, default=0.0, comment="重量 kg（自重动作填 0）")
    reps = db.Column(db.Integer, default=0, comment="次数")
    rpe = db.Column(db.Float, default=None, comment="主观强度 1-10")
    is_warmup = db.Column(db.Boolean, default=False, comment="是否热身组（不计入容量）")
    rest_sec = db.Column(db.Integer, default=None, comment="组间休息秒数")
    note = db.Column(db.String(128), default="", comment="备注")

    @property
    def volume(self):
        return round((self.weight_kg or 0) * (self.reps or 0), 1)

    @property
    def e1rm(self):
        """Epley 估算 1RM；次数为 1 时就是实际重量"""
        w, r = self.weight_kg or 0, self.reps or 0
        if w <= 0 or r <= 0:
            return 0.0
        if r == 1:
            return round(w, 1)
        return round(w * (1 + r / 30.0), 1)

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        d["volume"] = self.volume
        d["e1rm"] = self.e1rm
        return d


class PersonalRecord(db.Model, BaseModel):
    __tablename__ = "personal_records"
    __table_args__ = (
        db.UniqueConstraint("user_id", "exercise_name", "record_type",
                            name="uq_pr_user_exercise_type"),
    )

    user_id = db.Column(db.Integer, nullable=False, index=True, comment="用户 ID")
    exercise_id = db.Column(db.Integer, default=None, comment="动作库 ID")
    exercise_name = db.Column(db.String(64), nullable=False, comment="动作名")
    record_type = db.Column(db.String(16), nullable=False, comment="e1rm/max_weight/max_reps/max_volume")
    value = db.Column(db.Float, default=0.0, comment="纪录值")
    weight_kg = db.Column(db.Float, default=0.0, comment="达成时的重量")
    reps = db.Column(db.Integer, default=0, comment="达成时的次数")
    achieved_at = db.Column(db.DateTime, default=None, comment="达成时间")
    session_id = db.Column(db.Integer, default=None, comment="来源训练 ID")
    set_id = db.Column(db.Integer, default=None, comment="来源组 ID")

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        if isinstance(d.get("achieved_at"), datetime):
            d["achieved_at"] = d["achieved_at"].strftime("%Y-%m-%dT%H:%M:%SZ")
        return d
