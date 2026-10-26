# -*- coding: utf-8 -*-
"""教练认证：用户申请 / 进度查询 / 证件受保护读取 / 管理员审核 / 教练资料"""
import os
from datetime import datetime

from flask import jsonify, request, send_file

from models import db, utcnow
from models.auth import User
from models.coach import CoachApplication, CoachProfile
from utils.auth import require_auth, require_admin, require_coach
from services.private_files import save_credential_image, private_abs_path

from . import coaches_bp, admin_bp

CERT_TYPES = {"national": "国家职业资格", "ace": "ACE", "nssa": "NSCA-CPT", "other": "其他"}


# ---------------------------------------------------------------- 申请侧

@coaches_bp.route("/apply", methods=["POST"])
@require_auth
def apply_coach(user):
    """提交教练认证申请（multipart：3 个证件文件 + 表单字段）"""
    if user.is_coach:
        return jsonify(code=400, msg="你已经是认证教练，无需重复申请"), 400

    pending = CoachApplication.query.filter_by(user_id=user.id, status="pending").first()
    if pending:
        return jsonify(code=400, msg="已有待审核的申请，请耐心等待管理员处理"), 400

    data = request.form
    real_name = (data.get("real_name") or "").strip()
    phone = (data.get("phone") or "").strip()
    cert_type = (data.get("cert_type") or "").strip()
    bio = (data.get("bio") or "").strip()
    specialties = (data.get("specialties") or "").strip()

    if not real_name or len(real_name) > 64:
        return jsonify(code=400, msg="请填写真实姓名"), 400
    if not phone or len(phone) > 20:
        return jsonify(code=400, msg="请填写联系电话"), 400
    if cert_type not in CERT_TYPES:
        return jsonify(code=400, msg="请选择资质类型"), 400
    if len(bio) > 500:
        return jsonify(code=400, msg="简介不能超过 500 字"), 400
    if len(specialties) > 256:
        return jsonify(code=400, msg="专长标签过长"), 400

    files = {
        "id_card_front": request.files.get("id_card_front"),
        "id_card_back": request.files.get("id_card_back"),
        "cert_file": request.files.get("cert_file"),
    }
    saved = {}
    for field, fs in files.items():
        if fs is None or not fs.filename:
            labels = {"id_card_front": "身份证人像面", "id_card_back": "身份证国徽面", "cert_file": "资质凭证"}
            return jsonify(code=400, msg=f"请上传{labels[field]}"), 400
        rel, err = save_credential_image(user.id, fs)
        if err:
            return jsonify(code=400, msg=f"{field}: {err}"), 400
        saved[field] = rel

    app_row = CoachApplication(
        user_id=user.id,
        real_name=real_name,
        phone=phone,
        id_card_front=saved["id_card_front"],
        id_card_back=saved["id_card_back"],
        cert_type=cert_type,
        cert_file=saved["cert_file"],
        bio=bio or None,
        specialties=specialties or None,
        status="pending",
    )
    db.session.add(app_row)
    db.session.commit()
    return jsonify(code=0, msg="申请已提交，请等待管理员审核", data=app_row.to_dict()), 201


@coaches_bp.route("/my-application", methods=["GET"])
@require_auth
def my_application(user):
    """查我最新的认证申请（含驳回原因）与教练身份状态"""
    latest = (CoachApplication.query.filter_by(user_id=user.id)
              .order_by(CoachApplication.id.desc()).first())
    profile = CoachProfile.query.filter_by(user_id=user.id).first()
    return jsonify(code=0, msg="success", data={
        "is_coach": bool(user.is_coach),
        "application": latest.to_dict() if latest else None,
        "profile": profile.to_dict() if profile else None,
    })


@coaches_bp.route("/applications/<int:aid>/file/<kind>", methods=["GET"])
@require_auth
def application_file(user, aid, kind):
    """证件图片受保护读取：仅申请人本人和管理员可看，绝不走静态目录"""
    if kind not in ("front", "back", "cert"):
        return jsonify(code=404, msg="未知文件类型"), 404
    app_row = db.session.get(CoachApplication, aid)
    if app_row is None:
        return jsonify(code=404, msg="申请不存在"), 404
    if not (user.is_admin or app_row.user_id == user.id):
        return jsonify(code=403, msg="无权限查看该证件"), 403

    rel = {"front": app_row.id_card_front, "back": app_row.id_card_back, "cert": app_row.cert_file}[kind]
    abs_path = private_abs_path(rel)
    if abs_path is None or not os.path.exists(abs_path):
        return jsonify(code=404, msg="文件不存在"), 404
    return send_file(abs_path, conditional=True)


# ---------------------------------------------------------------- 教练工作台（M2）

@coaches_bp.route("/profile", methods=["GET"])
@require_coach
def coach_profile(user):
    profile = CoachProfile.query.filter_by(user_id=user.id).first()
    if profile is None and user.is_admin:
        # 管理员预览：没有档案就给空壳
        return jsonify(code=0, msg="success", data=None)
    if profile is None:
        return jsonify(code=404, msg="教练档案不存在"), 404
    return jsonify(code=0, msg="success", data=profile.to_dict())


@coaches_bp.route("/profile", methods=["PATCH"])
@require_coach
def update_coach_profile(user):
    profile = CoachProfile.query.filter_by(user_id=user.id).first()
    if profile is None:
        return jsonify(code=404, msg="教练档案不存在"), 404
    data = request.get_json(silent=True) or {}
    if "display_name" in data:
        name = (data["display_name"] or "").strip()
        if not name or len(name) > 64:
            return jsonify(code=400, msg="展示名不能为空且不超过 64 字"), 400
        profile.display_name = name
    if "bio" in data:
        bio = (data["bio"] or "").strip()
        if len(bio) > 500:
            return jsonify(code=400, msg="简介不能超过 500 字"), 400
        profile.bio = bio
    if "specialties" in data:
        sp = (data["specialties"] or "").strip()
        if len(sp) > 256:
            return jsonify(code=400, msg="专长标签过长"), 400
        profile.specialties = sp
    if "years" in data:
        try:
            years = int(data["years"])
        except (TypeError, ValueError):
            return jsonify(code=400, msg="执教年限必须是数字"), 400
        if not 0 <= years <= 60:
            return jsonify(code=400, msg="执教年限应在 0-60 之间"), 400
        profile.years = years
    if "avatar_url" in data:
        profile.avatar_url = (data["avatar_url"] or "").strip() or None
    db.session.commit()
    return jsonify(code=0, msg="资料已更新", data=profile.to_dict())


@coaches_bp.route("/dashboard", methods=["GET"])
@require_coach
def coach_dashboard(user):
    profile = CoachProfile.query.filter_by(user_id=user.id).first()
    latest = (CoachApplication.query.filter_by(user_id=user.id, status="approved")
              .order_by(CoachApplication.id.desc()).first())
    days = None
    if latest and latest.reviewed_at:
        days = max((utcnow() - latest.reviewed_at).days, 0)
    return jsonify(code=0, msg="success", data={
        "profile": profile.to_dict() if profile else None,
        "certified_days": days,
        "students": None,   # M3 上线学员体系后替换为真实数据
        "plans_count": 0,   # M2 后续支持教练发布计划后替换
    })


# ---------------------------------------------------------------- 管理员审核

@admin_bp.route("/coach-applications", methods=["GET"])
@require_admin
def admin_coach_applications(user):
    status = request.args.get("status", "pending")
    if status not in ("pending", "approved", "rejected", "all"):
        status = "pending"
    page = max(request.args.get("page", 1, type=int), 1)
    page_size = min(max(request.args.get("page_size", 20, type=int), 1), 100)

    q = CoachApplication.query.order_by(CoachApplication.id.desc())
    if status != "all":
        q = q.filter_by(status=status)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    user_ids = {it.user_id for it in items}
    users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}
    result = []
    for it in items:
        d = it.to_dict()
        u = users.get(it.user_id)
        d["user_nickname"] = u.nickname if u else ""
        d["user_email"] = u.email if u else ""
        d["user_is_coach"] = bool(u.is_coach) if u else False
        result.append(d)
    return jsonify(code=0, msg="success", data={
        "items": result, "total": total, "page": page, "page_size": page_size,
    })


@admin_bp.route("/coach-applications/<int:aid>/approve", methods=["PUT"])
@require_admin
def admin_approve_coach(user, aid):
    app_row = db.session.get(CoachApplication, aid)
    if app_row is None:
        return jsonify(code=404, msg="申请不存在"), 404
    if app_row.status != "pending":
        return jsonify(code=400, msg="该申请已处理"), 400

    applicant = db.session.get(User, app_row.user_id)
    if applicant is None:
        return jsonify(code=400, msg="申请人账号不存在"), 400

    profile = CoachProfile.query.filter_by(user_id=app_row.user_id).first()
    if profile is None:
        profile = CoachProfile(user_id=app_row.user_id)
        db.session.add(profile)
    profile.display_name = applicant.nickname or app_row.real_name
    profile.bio = app_row.bio
    profile.specialties = app_row.specialties
    profile.cert_type = app_row.cert_type
    profile.avatar_url = applicant.avatar_url
    profile.status = "active"

    applicant.is_coach = True
    app_row.status = "approved"
    app_row.reviewer_id = user.id
    app_row.reviewed_at = utcnow()
    db.session.commit()
    return jsonify(code=0, msg="已通过认证", data=app_row.to_dict())


@admin_bp.route("/coach-applications/<int:aid>/reject", methods=["PUT"])
@require_admin
def admin_reject_coach(user, aid):
    app_row = db.session.get(CoachApplication, aid)
    if app_row is None:
        return jsonify(code=404, msg="申请不存在"), 404
    if app_row.status != "pending":
        return jsonify(code=400, msg="该申请已处理"), 400
    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify(code=400, msg="请填写驳回原因（申请人会在个人中心看到）"), 400

    app_row.status = "rejected"
    app_row.reject_reason = reason[:256]
    app_row.reviewer_id = user.id
    app_row.reviewed_at = utcnow()
    db.session.commit()
    return jsonify(code=0, msg="已驳回", data=app_row.to_dict())
