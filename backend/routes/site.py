from flask import jsonify
from . import site_bp
from models.site import SiteInfo
from models import db


@site_bp.route("/contact-info", methods=["GET"])
def get_contact_info():
    info = SiteInfo.query.order_by(SiteInfo.id).first()
    if not info:
        return jsonify(code=0, msg="success", data={
            "address": "上海市静安区南京西路1788号久光中心 12F",
            "phone": "+86 21 6188 3000",
            "email": "hello@fitluxe.com",
            "business_hours": {"weekday": "7:00 – 22:00", "weekend": "8:00 – 20:00"},
            "social_media": [
                {"platform": "wechat", "name": "微信"},
                {"platform": "weibo", "name": "微博"},
                {"platform": "xiaohongshu", "name": "小红书"},
                {"platform": "douyin", "name": "抖音"},
            ],
        })
    return jsonify(code=0, msg="success", data=info.to_dict())
