# -*- coding: utf-8 -*-
"""成就勋章接口。只读，不写库。"""

from flask import jsonify

from models import db
from routes import achievements_bp
from services.achievement import achievement_list
from utils.auth import require_auth


@achievements_bp.route("", methods=["GET"])
@require_auth
def list_achievements(user):
    """全部成就 + 汇总。未登录返回 401，不再回落到 user_id=0 的公共数据。"""
    return jsonify(code=0, msg="success", data=achievement_list(user.id))
