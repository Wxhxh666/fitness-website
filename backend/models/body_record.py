from datetime import date
from . import db, BaseModel


class BodyRecord(db.Model, BaseModel):
    """身材数据快照：每次「一键保存」生成一条完整记录，支撑趋势图、对比与导出"""
    __tablename__ = "body_records"

    user_id = db.Column(db.Integer, default=0, comment="用户 ID")
    record_date = db.Column(db.Date, default=date.today, comment="记录日期")
    stage = db.Column(db.String(16), comment="阶段: fatloss/muscle/maintain")
    gender = db.Column(db.String(8), default="male", comment="性别")
    age = db.Column(db.Integer, comment="年龄")
    activity_level = db.Column(db.String(16), default="light", comment="运动强度")

    # 原始输入
    height_cm = db.Column(db.Float, comment="身高 cm")
    weight_kg = db.Column(db.Float, comment="体重 kg")
    waist_cm = db.Column(db.Float, comment="腰围 cm")
    hip_cm = db.Column(db.Float, comment="臀围 cm")
    neck_cm = db.Column(db.Float, comment="颈围 cm")
    chest_cm = db.Column(db.Float, comment="胸围 cm")
    shoulder_cm = db.Column(db.Float, comment="肩宽 cm")
    thigh_cm = db.Column(db.Float, comment="大腿围 cm")
    arm_cm = db.Column(db.Float, comment="手臂围 cm")
    calf_cm = db.Column(db.Float, comment="小腿围 cm")

    # 计算结果
    bmi = db.Column(db.Float, comment="BMI")
    body_fat = db.Column(db.Float, comment="体脂率 %")
    bmr = db.Column(db.Float, comment="基础代谢 kcal")
    tdee = db.Column(db.Float, comment="每日总消耗 kcal")
    whr = db.Column(db.Float, comment="腰臀比")
    muscle_mass = db.Column(db.Float, comment="肌肉量估算 kg")
    standard_weight = db.Column(db.Float, comment="标准体重 kg")

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        if isinstance(self.record_date, date):
            d["record_date"] = self.record_date.strftime("%Y-%m-%d")
        return d


class BodyGoal(db.Model, BaseModel):
    """目标身材设定"""
    __tablename__ = "body_goals"

    user_id = db.Column(db.Integer, default=0, comment="用户 ID")
    target_weight = db.Column(db.Float, comment="目标体重 kg")
    target_bmi = db.Column(db.Float, comment="目标 BMI")
    target_body_fat = db.Column(db.Float, comment="目标体脂率 %")
    daily_calorie = db.Column(db.Float, comment="每日目标摄入 kcal")


class BodyProfile(db.Model, BaseModel):
    """个人基础档案：性别 / 年龄 / 运动强度 / 单位制"""
    __tablename__ = "body_profiles"

    user_id = db.Column(db.Integer, default=0, unique=True, comment="用户 ID")
    gender = db.Column(db.String(8), default="male", comment="性别")
    age = db.Column(db.Integer, default=25, comment="年龄")
    activity_level = db.Column(db.String(16), default="light", comment="运动强度")
    unit_system = db.Column(db.String(8), default="metric", comment="单位制 metric/imperial")
