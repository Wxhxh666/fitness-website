# -*- coding: utf-8 -*-
from . import db, BaseModel


class UserPlan(db.Model, BaseModel):
    __tablename__ = "user_plans"

    user_id = db.Column(db.Integer, nullable=False, comment="用户 ID")
    name = db.Column(db.String(100), nullable=False, comment="计划名称")
    goal = db.Column(db.String(32), default="", comment="目标")
    description = db.Column(db.Text, comment="计划描述")
    duration = db.Column(db.String(32), comment="周期")
    frequency = db.Column(db.String(32), comment="频次")
    difficulty = db.Column(db.String(16), default="intermediate", comment="难度")
    difficulty_label = db.Column(db.String(8), default="中级", comment="难度中文名")
    focus_tags = db.Column(db.JSON, comment="专注标签")
    cover_url = db.Column(db.String(256), comment="封面图")
    weekly_schedule = db.Column(db.JSON, comment="周训安排")
    is_active = db.Column(db.Boolean, default=True)
    source_plan_id = db.Column(db.Integer, default=None, comment="来源官方计划ID")

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        d["desc"] = d.pop("description", "")
        return d


# 说明：原来的 TrainingLog（一天一条 + JSON 动作列表）已由
# models/workout.py 的 WorkoutSession / WorkoutSet 取代，
# 数据迁移见 migrations/versions/*_migrate_training_logs_to_workout_sessions.py。
