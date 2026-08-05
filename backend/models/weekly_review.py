from . import db, BaseModel, datetime


class WeeklyReview(db.Model, BaseModel):
    """AI 周复盘记录表"""
    __tablename__ = "weekly_reviews"

    user_id = db.Column(db.Integer, nullable=False, index=True, comment="用户 ID")
    week_start = db.Column(db.String(10), nullable=False, comment="周起始日期(周一)")
    review_text = db.Column(db.Text, comment="复盘文本")
    summary_json = db.Column(db.JSON, comment="周统计摘要")
    model = db.Column(db.String(64), default="", comment="生成模型")
