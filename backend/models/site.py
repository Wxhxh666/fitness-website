from . import db, BaseModel


class SiteInfo(db.Model, BaseModel):
    __tablename__ = "site_info"

    address = db.Column(db.String(256), comment="地址")
    phone = db.Column(db.String(32), comment="联系电话")
    email = db.Column(db.String(100), comment="邮箱")
    business_hours = db.Column(db.JSON, comment='营业时间 {"weekday":"...","weekend":"..."}')
    social_media = db.Column(db.JSON, comment="社交媒体列表")
