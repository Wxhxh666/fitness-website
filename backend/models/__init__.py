from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timezone

db = SQLAlchemy()


def utcnow():
    """
    统一的“当前 UTC 时间”，返回 naive datetime 以匹配 MySQL DATETIME 列。
    不要再用 datetime.utcnow()（Python 3.12 起已弃用），也不要和 date.today() 混用——
    一个 UTC 一个本地时区，跨零点会产生“打卡算到前一天”这类边界 bug。
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BaseModel:
    """Mixin with common fields."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    def to_dict(self, exclude=None):
        exclude = exclude or []
        d = {}
        for col in self.__table__.columns:
            if col.name not in exclude:
                val = getattr(self, col.name)
                if isinstance(val, datetime):
                    val = val.strftime("%Y-%m-%dT%H:%M:%SZ")
                d[col.name] = val
        return d

    def from_dict(self, data):
        for col in self.__table__.columns:
            if col.name in data and col.name not in ("id", "created_at", "updated_at"):
                setattr(self, col.name, data[col.name])
        return self

from .user_plan import UserPlan
from .body_record import BodyRecord, BodyGoal, BodyProfile
from .diet_plan import DietPlan
from .diet_log import DietLog
from .auth import User, VerificationCode
from .body_metric import BodyMetric
from .contact import ContactMessage
from .exercise import Exercise, ExerciseCategory
from .plan import Plan, PlanGoal
from .profile_request import ProfileChangeRequest
from .site import SiteInfo
from .weekly_review import WeeklyReview
from .workout import WorkoutSession, WorkoutSet, PersonalRecord
