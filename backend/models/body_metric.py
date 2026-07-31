from . import db, BaseModel, datetime


class BodyMetric(db.Model, BaseModel):
    __tablename__ = "body_metrics"

    user_id = db.Column(db.Integer, default=0, comment="用户 ID")
    key = db.Column(db.String(32), nullable=False, comment="指标 key: weight/body_fat/muscle_mass/bmr/chest/waist/hips/arm/thigh/calf")
    label = db.Column(db.String(32), nullable=False, comment="中文名")
    value = db.Column(db.Float, nullable=False, comment="当前值")
    unit = db.Column(db.String(16), default="cm", comment="单位")
    change = db.Column(db.Float, default=0.0, comment="变化量")
    trend = db.Column(db.String(8), default="up", comment="趋势 up/down")
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, comment="记录时间")
