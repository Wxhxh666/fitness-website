# -*- coding: utf-8 -*-
from . import db, BaseModel, datetime


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


class TrainingLog(db.Model, BaseModel):
    __tablename__ = "training_logs"

    user_id = db.Column(db.Integer, nullable=False, comment="用户 ID")
    plan_id = db.Column(db.Integer, nullable=False, comment="计划 ID")
    is_official = db.Column(db.Boolean, default=False, comment="是否官方计划")
    log_date = db.Column(db.Date, nullable=False, comment="训练日期")
    focus = db.Column(db.String(32), comment="训练重点")
    exercises = db.Column(db.JSON, comment="完成动作列表")
    note = db.Column(db.Text, comment="备注")

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        if isinstance(d.get("log_date"), datetime):
            d["log_date"] = d["log_date"].strftime("%Y-%m-%d")
        return d
