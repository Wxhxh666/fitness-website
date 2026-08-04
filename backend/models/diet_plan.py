from . import db, BaseModel


class DietPlan(db.Model, BaseModel):
    """AI 饮食方案存档"""
    __tablename__ = "diet_plans"

    user_id = db.Column(db.Integer, default=0, comment="用户 ID")
    target = db.Column(db.String(16), default="fatloss", comment="目标: fatloss/muscle/maintain")
    sport_level = db.Column(db.String(32), comment="运动强度")
    diet_limit = db.Column(db.String(256), comment="饮食限制与偏好")
    eat_scene = db.Column(db.String(64), comment="就餐条件")
    plan_json = db.Column(db.Text, comment="结构化方案 JSON")
    raw_text = db.Column(db.Text, comment="模型原始输出")
    model = db.Column(db.String(64), comment="模型名称")
