from . import db, BaseModel, utcnow


class User(db.Model, BaseModel):
    __tablename__ = "users"

    phone = db.Column(db.String(20), unique=True, nullable=True, comment="手机号")
    email = db.Column(db.String(100), unique=True, nullable=True, comment="邮箱")
    password_hash = db.Column(db.String(256), comment="密码哈希")
    nickname = db.Column(db.String(50), comment="昵称")
    avatar_url = db.Column(db.String(256), comment="头像URL")
    ai_model = db.Column(db.String(32), default="deepseek-flash", comment="默认AI模型")
    unit_system = db.Column(db.String(16), default="metric", comment="度量单位")
    notification_enabled = db.Column(db.Boolean, default=True, comment="通知开关")
    is_active = db.Column(db.Boolean, default=True, comment="是否启用")
    is_admin = db.Column(db.Boolean, default=False, comment="是否管理员")
    is_coach = db.Column(db.Boolean, default=False, nullable=False, comment="是否认证教练", index=True)
    last_login_at = db.Column(db.DateTime, nullable=True, comment="最后登录时间")

    def to_dict(self, exclude=None):
        exclude = exclude or ["password_hash"]
        return super().to_dict(exclude)


class VerificationCode(db.Model, BaseModel):
    __tablename__ = "verification_codes"

    identifier = db.Column(db.String(100), nullable=False, comment="手机号或邮箱")
    code = db.Column(db.String(6), nullable=False, comment="验证码")
    purpose = db.Column(db.String(16), default="login", comment="用途: login/register")
    is_used = db.Column(db.Boolean, default=False, comment="是否已使用")
    expires_at = db.Column(db.DateTime, nullable=False, comment="过期时间(UTC)")

    def is_expired(self):
        return utcnow() > self.expires_at
