from . import db, BaseModel, datetime


class ContactMessage(db.Model, BaseModel):
    __tablename__ = "contact_messages"

    name = db.Column(db.String(50), nullable=False, comment="姓名")
    email = db.Column(db.String(100), nullable=False, comment="邮箱")
    phone = db.Column(db.String(20), comment="电话")
    subject = db.Column(db.String(32), nullable=False, comment="主题枚举")
    message = db.Column(db.Text, nullable=False, comment="留言内容")
    is_read = db.Column(db.Boolean, default=False, comment="是否已读")
