from . import db, BaseModel, datetime


class PlanGoal(db.Model, BaseModel):
    __tablename__ = "plan_goals"

    key = db.Column(db.String(32), unique=True, nullable=False, comment="目标标识")
    label = db.Column(db.String(32), nullable=False, comment="中文名称")
    description = db.Column(db.String(128), comment="简短描述")
    sort_order = db.Column(db.Integer, default=0)


class Plan(db.Model, BaseModel):
    __tablename__ = "plans"

    name = db.Column(db.String(100), nullable=False, comment="计划名称")
    goal = db.Column(db.String(32), nullable=False, comment="目标 key")
    badge = db.Column(db.String(16), default="推荐", comment="标签")
    description = db.Column(db.Text, comment="计划描述")
    duration = db.Column(db.String(32), comment="周期")
    frequency = db.Column(db.String(32), comment="频次")
    difficulty = db.Column(db.String(16), default="intermediate", comment="难度")
    difficulty_label = db.Column(db.String(8), default="中级", comment="难度中文名")
    focus_tags = db.Column(db.JSON, comment="专注标签数组")
    cover_url = db.Column(db.String(256), comment="封面图")
    weekly_schedule = db.Column(db.JSON, comment="周训安排")
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        d["desc"] = d.pop("description", "")
        d["focus"] = d.pop("focus_tags", [])
        return d
