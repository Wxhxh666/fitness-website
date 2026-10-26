# -*- coding: utf-8 -*-
"""教练认证：用户申请 / 进度查询 / 证件受保护读取 / 管理员审核 / 教练资料

M3 学员体系：教练列表、绑定关系（申请/接受/拒绝/解绑）、学员训练数据
概览（仅 active 关系）、站内咨询留言。
"""
import os
from datetime import datetime

from flask import jsonify, request, send_file
from sqlalchemy import or_, and_

from models import db, utcnow
from models.auth import User
from models.coach import CoachApplication, CoachProfile, CoachStudent, CoachMessage
from models.workout import WorkoutSession
from utils.auth import require_auth, require_admin, require_coach
from services.private_files import save_credential_image, private_abs_path
from services import workout as workout_svc

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
    active = CoachStudent.query.filter_by(coach_user_id=user.id, status="active")
    unread_count = 0
    for rel in active.all():
        unread_count += _unread_count(rel, user.id)
    return jsonify(code=0, msg="success", data={
        "profile": profile.to_dict() if profile else None,
        "certified_days": days,
        "students_active": CoachStudent.query.filter_by(
            coach_user_id=user.id, status="active").count(),
        "students_pending": CoachStudent.query.filter_by(
            coach_user_id=user.id, status="pending").count(),
        "unread_total": unread_count,
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


# ================================================================ M3 学员体系

def _unread_count(relation, viewer_id):
    """某段关系里 viewer 未读的消息数（对方发的、还没读的）"""
    return CoachMessage.query.filter(
        CoachMessage.coach_user_id == relation.coach_user_id,
        CoachMessage.student_user_id == relation.student_user_id,
        CoachMessage.sender_id != viewer_id,
        CoachMessage.read_at.is_(None),
    ).count()


def _user_brief(uid):
    u = db.session.get(User, uid)
    if u is None:
        return None
    return {"id": u.id, "nickname": u.nickname, "avatar_url": u.avatar_url}


# ---------------------------------------------------------------- 教练列表（用户侧）

@coaches_bp.route("", methods=["GET"])
@require_auth
def coach_list(user):
    """在营教练列表（供用户浏览并申请绑定），带我与每位教练的绑定状态"""
    profiles = (CoachProfile.query.filter_by(status="active")
                .order_by(CoachProfile.id.asc()).all())
    coach_uids = [p.user_id for p in profiles]
    users = {u.id: u for u in User.query.filter(User.id.in_(coach_uids)).all()} if coach_uids else {}

    mine = CoachStudent.query.filter_by(student_user_id=user.id).all()
    rel_map = {r.coach_user_id: r for r in mine}

    counts = {}
    if coach_uids:
        rows = (db.session.query(CoachStudent.coach_user_id, db.func.count())
                .filter(CoachStudent.coach_user_id.in_(coach_uids),
                        CoachStudent.status == "active")
                .group_by(CoachStudent.coach_user_id).all())
        counts = {r[0]: r[1] for r in rows}

    items = []
    for p in profiles:
        d = p.to_dict()
        u = users.get(p.user_id)
        d["nickname"] = u.nickname if u else ""
        rel = rel_map.get(p.user_id)
        d["relation"] = ({"id": rel.id, "status": rel.status} if rel else None)
        d["students_count"] = counts.get(p.user_id, 0)
        items.append(d)
    return jsonify(code=0, msg="success", data={"items": items})


@coaches_bp.route("/<int:coach_uid>/subscribe", methods=["POST"])
@require_auth
def subscribe_coach(user, coach_uid):
    """申请绑定教练（active 后教练可查看我的训练数据概览）"""
    if coach_uid == user.id:
        return jsonify(code=400, msg="不能绑定自己"), 400
    coach_user = db.session.get(User, coach_uid)
    if coach_user is None or not coach_user.is_coach:
        return jsonify(code=404, msg="该教练不存在或未认证"), 404
    profile = CoachProfile.query.filter_by(user_id=coach_uid, status="active").first()
    if profile is None:
        return jsonify(code=400, msg="该教练当前不在营业状态"), 400

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if len(message) > 256:
        return jsonify(code=400, msg="留言不能超过 256 字"), 400

    rel = CoachStudent.query.filter_by(coach_user_id=coach_uid, student_user_id=user.id).first()
    if rel and rel.status in ("pending", "active"):
        return jsonify(code=400, msg="你们已存在绑定或待处理的申请"), 400
    if rel is None:
        rel = CoachStudent(coach_user_id=coach_uid, student_user_id=user.id)
        db.session.add(rel)
    rel.status = "pending"
    rel.message = message or None
    rel.reject_reason = None
    rel.responded_at = None
    db.session.commit()
    return jsonify(code=0, msg="申请已发送，等待教练确认", data=rel.to_dict()), 201


@coaches_bp.route("/mine", methods=["GET"])
@require_auth
def my_coaches(user):
    """我（学员视角）的教练关系列表，含未读消息数"""
    rels = (CoachStudent.query.filter_by(student_user_id=user.id)
            .order_by(CoachStudent.id.desc()).all())
    items = []
    for r in rels:
        d = r.to_dict()
        d["coach"] = _user_brief(r.coach_user_id)
        profile = CoachProfile.query.filter_by(user_id=r.coach_user_id).first()
        d["coach_display_name"] = profile.display_name if profile else ""
        d["unread"] = _unread_count(r, user.id) if r.status == "active" else 0
        items.append(d)
    return jsonify(code=0, msg="success", data={"items": items})


@coaches_bp.route("/mine/<int:coach_uid>", methods=["DELETE"])
@require_auth
def terminate_coach(user, coach_uid):
    """学员解绑（active → terminated）；pending 状态则视为撤回申请，直接删除"""
    rel = CoachStudent.query.filter_by(coach_user_id=coach_uid, student_user_id=user.id).first()
    if rel is None:
        return jsonify(code=404, msg="不存在与该教练的绑定关系"), 404
    if rel.status == "pending":
        db.session.delete(rel)
        db.session.commit()
        return jsonify(code=0, msg="已撤回申请")
    if rel.status != "active":
        return jsonify(code=400, msg="当前状态无需操作"), 400
    rel.status = "terminated"
    rel.responded_at = utcnow()
    db.session.commit()
    return jsonify(code=0, msg="已解除绑定")


# ---------------------------------------------------------------- 学员管理（教练侧）

@coaches_bp.route("/students", methods=["GET"])
@require_coach
def coach_students(user):
    """我的学员关系列表（申请/在学/已终止），含未读消息数"""
    status = request.args.get("status", "all")
    if status not in ("pending", "active", "terminated", "all"):
        status = "all"
    q = CoachStudent.query.filter_by(coach_user_id=user.id)
    if status != "all":
        q = q.filter_by(status=status)
    rels = q.order_by(CoachStudent.id.desc()).all()
    items = []
    for r in rels:
        d = r.to_dict()
        d["student"] = _user_brief(r.student_user_id)
        d["unread"] = _unread_count(r, user.id) if r.status == "active" else 0
        items.append(d)
    pending_total = CoachStudent.query.filter_by(coach_user_id=user.id, status="pending").count()
    return jsonify(code=0, msg="success", data={
        "items": items, "pending_total": pending_total,
    })


def _load_relation(rid, user):
    """加载绑定关系并校验访问者是其中一方"""
    rel = db.session.get(CoachStudent, rid)
    if rel is None:
        return None, (jsonify(code=404, msg="绑定关系不存在"), 404)
    if user.id not in (rel.coach_user_id, rel.student_user_id) and not user.is_admin:
        return None, (jsonify(code=403, msg="无权限访问该绑定关系"), 403)
    return rel, None


@coaches_bp.route("/students/<int:rid>/accept", methods=["PUT"])
@require_coach
def accept_student(user, rid):
    rel, err = _load_relation(rid, user)
    if err:
        return err
    if user.id != rel.coach_user_id:
        return jsonify(code=403, msg="只有教练本人可以处理申请"), 403
    if rel.status != "pending":
        return jsonify(code=400, msg="该申请已处理"), 400
    rel.status = "active"
    rel.responded_at = utcnow()
    db.session.commit()
    return jsonify(code=0, msg="已接受，学员已加入你的学员列表", data=rel.to_dict())


@coaches_bp.route("/students/<int:rid>/reject", methods=["PUT"])
@require_coach
def reject_student(user, rid):
    rel, err = _load_relation(rid, user)
    if err:
        return err
    if user.id != rel.coach_user_id:
        return jsonify(code=403, msg="只有教练本人可以处理申请"), 403
    if rel.status != "pending":
        return jsonify(code=400, msg="该申请已处理"), 400
    data = request.get_json(silent=True) or {}
    reason = (data.get("reason") or "").strip()
    if not reason:
        return jsonify(code=400, msg="请填写拒绝原因（学员会在申请状态里看到）"), 400
    rel.status = "terminated"
    rel.reject_reason = reason[:256]
    rel.responded_at = utcnow()
    db.session.commit()
    return jsonify(code=0, msg="已拒绝", data=rel.to_dict())


@coaches_bp.route("/students/<int:rid>/overview", methods=["GET"])
@require_coach
def student_overview(user, rid):
    """学员训练数据概览：仅 active 关系开放（学员申请绑定即同意）"""
    rel, err = _load_relation(rid, user)
    if err:
        return err
    if user.id != rel.coach_user_id and not user.is_admin:
        return jsonify(code=403, msg="只有教练本人可以查看学员数据"), 403
    if rel.status != "active":
        return jsonify(code=403, msg="仅对已确认绑定的学员开放数据查看"), 403

    uid = rel.student_user_id
    recent = (WorkoutSession.query.filter_by(user_id=uid)
              .order_by(WorkoutSession.session_date.desc(), WorkoutSession.id.desc())
              .limit(8).all())
    data = {
        "student": _user_brief(uid),
        "binding": {"id": rel.id, "created_at": rel.created_at.isoformat() if rel.created_at else None},
        "overview": workout_svc.overview(uid),
        "weekly_volume": workout_svc.weekly_volume_series(uid, weeks=8),
        "recent_sessions": [workout_svc.session_brief(s) for s in recent],
    }
    return jsonify(code=0, msg="success", data=data)


# ---------------------------------------------------------------- 站内咨询

@coaches_bp.route("/students/<int:rid>/messages", methods=["GET"])
@require_auth
def list_messages(user, rid):
    """某段绑定关系的消息记录（增量拉取：after_id），并顺带把对方发来的标为已读"""
    rel, err = _load_relation(rid, user)
    if err:
        return err
    if rel.status != "active":
        return jsonify(code=400, msg="仅已确认绑定的双方可以咨询留言"), 400

    after_id = request.args.get("after_id", 0, type=int)
    limit = min(max(request.args.get("limit", 100, type=int), 1), 200)
    q = CoachMessage.query.filter(
        CoachMessage.coach_user_id == rel.coach_user_id,
        CoachMessage.student_user_id == rel.student_user_id,
        CoachMessage.id > after_id,
    ).order_by(CoachMessage.id.asc()).limit(limit)
    msgs = q.all()
    # 把对方发给我的标为已读
    unread_ids = [m.id for m in msgs if m.sender_id != user.id and m.read_at is None]
    if unread_ids:
        CoachMessage.query.filter(CoachMessage.id.in_(unread_ids)).update(
            {CoachMessage.read_at: utcnow()}, synchronize_session=False)
        db.session.commit()
    return jsonify(code=0, msg="success", data={
        "relation": {"id": rel.id, "coach_user_id": rel.coach_user_id,
                     "student_user_id": rel.student_user_id, "status": rel.status},
        "me": user.id,
        "items": [m.to_dict() for m in msgs],
    })


@coaches_bp.route("/students/<int:rid>/messages", methods=["POST"])
@require_auth
def send_message(user, rid):
    rel, err = _load_relation(rid, user)
    if err:
        return err
    if rel.status != "active":
        return jsonify(code=400, msg="仅已确认绑定的双方可以咨询留言"), 400
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify(code=400, msg="消息内容不能为空"), 400
    if len(content) > 1000:
        return jsonify(code=400, msg="消息不能超过 1000 字"), 400
    msg = CoachMessage(
        coach_user_id=rel.coach_user_id,
        student_user_id=rel.student_user_id,
        sender_id=user.id,
        content=content,
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify(code=0, msg="已发送", data=msg.to_dict()), 201


@coaches_bp.route("/unread-total", methods=["GET"])
@require_auth
def unread_total(user):
    """当前用户所有 active 咨询会话的未读总数（导航角标用）"""
    active = CoachStudent.query.filter(
        CoachStudent.status == "active",
        or_(CoachStudent.coach_user_id == user.id,
            CoachStudent.student_user_id == user.id),
    ).subquery()
    total = (CoachMessage.query
             .join(active, db.and_(
                 CoachMessage.coach_user_id == active.c.coach_user_id,
                 CoachMessage.student_user_id == active.c.student_user_id))
             .filter(CoachMessage.sender_id != user.id,
                     CoachMessage.read_at.is_(None))
             .count())
    return jsonify(code=0, msg="success", data={"total": total})
