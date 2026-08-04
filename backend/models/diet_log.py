from datetime import date
from . import db, BaseModel


class DietLog(db.Model, BaseModel):
    """每日饮食打卡：记录当日摄入热量与三大营养素"""
    __tablename__ = "diet_logs"

    user_id = db.Column(db.Integer, default=0, comment="用户 ID")
    log_date = db.Column(db.Date, default=date.today, comment="打卡日期")
    calories = db.Column(db.Float, comment="当日摄入热量 kcal")
    protein_g = db.Column(db.Float, comment="蛋白质 g")
    carbs_g = db.Column(db.Float, comment="碳水 g")
    fat_g = db.Column(db.Float, comment="脂肪 g")
    note = db.Column(db.String(256), comment="备注")

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        if isinstance(self.log_date, date):
            d["log_date"] = self.log_date.strftime("%Y-%m-%d")
        return d
