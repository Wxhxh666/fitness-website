from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class BaseModel:
    """Mixin with common fields."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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

from .user_plan import UserPlan, TrainingLog
