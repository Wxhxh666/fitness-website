from . import db, BaseModel, datetime


class User(db.Model, BaseModel):
    __tablename__ = "users"

    phone = db.Column(db.String(20), unique=True, nullable=True, comment="是否管理员")
    email = db.Column(db.String(100), unique=True, nullable=True, comment="是否管理员")
    password_hash = db.Column(db.String(256), comment="是否管理员")
    nickname = db.Column(db.String(50), comment="是否管理员")
    avatar_url = db.Column(db.String(256), comment="是否管理员")
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False, comment="是否管理员")
    last_login_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self, exclude=None):
        exclude = exclude or ["password_hash"]
        return super().to_dict(exclude)


class VerificationCode(db.Model, BaseModel):
    __tablename__ = "verification_codes"

    identifier = db.Column(db.String(100), nullable=False, comment="是否管理员")
    code = db.Column(db.String(6), nullable=False, comment="是否管理员")
    purpose = db.Column(db.String(16), default="login", comment="是否管理员")
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False, comment="是否管理员")

    def is_expired(self):
        return datetime.utcnow() > self.expires_at
