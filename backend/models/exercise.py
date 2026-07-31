from . import db, BaseModel, datetime


class ExerciseCategory(db.Model, BaseModel):
    __tablename__ = "exercise_categories"

    key = db.Column(db.String(32), unique=True, nullable=False, comment="分类标识")
    label = db.Column(db.String(32), nullable=False, comment="中文名称")
    sort_order = db.Column(db.Integer, default=0, comment="排序")
    is_active = db.Column(db.Boolean, default=True)


class Exercise(db.Model, BaseModel):
    __tablename__ = "exercises"

    name = db.Column(db.String(100), nullable=False, comment="动作名称")
    category = db.Column(db.String(32), nullable=False, comment="分类 key")
    category_label = db.Column(db.String(32), nullable=False, comment="分类中文名")
    description = db.Column(db.Text, comment="动作描述")
    difficulty = db.Column(db.String(16), default="intermediate", comment="难度: beginner/intermediate/advanced")
    difficulty_label = db.Column(db.String(8), default="中级", comment="难度中文名")
    duration = db.Column(db.String(64), comment="建议组数")
    cover_url = db.Column(db.String(256), comment="封面图")
    video_url = db.Column(db.String(256), comment="教学视频")
    steps = db.Column(db.JSON, comment="步骤列表 [{order, content}]")
    target_muscles = db.Column(db.JSON, comment="目标肌群")
    tips = db.Column(db.JSON, comment="注意事项")
    sort_order = db.Column(db.Integer, default=0, comment="排序权重")
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self, exclude=None):
        d = super().to_dict(exclude)
        d["desc"] = d.pop("description", "")
        return d
