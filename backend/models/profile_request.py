from . import db, BaseModel

class ProfileChangeRequest(db.Model, BaseModel):
    __tablename__ = "profile_change_requests"
    user_id = db.Column(db.Integer, nullable=False)
    field_name = db.Column(db.String(32), nullable=False)
    old_value = db.Column(db.String(256))
    new_value = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(16), default="pending")
    remark = db.Column(db.String(256))
