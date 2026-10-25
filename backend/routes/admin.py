from flask import Blueprint, jsonify, request
from models import db
from models.auth import User
from models.exercise import Exercise, ExerciseCategory
from models.plan import Plan, PlanGoal
from models.body_metric import BodyMetric
from models.contact import ContactMessage
from utils.auth import require_admin

from . import admin_bp


@admin_bp.route("/dashboard", methods=["GET"])
@require_admin
def dashboard(user):
    users_count = User.query.count()
    messages_count = ContactMessage.query.count()
    unread = ContactMessage.query.filter_by(is_read=False).count()
    exercises_count = Exercise.query.filter_by(is_active=True).count()
    plans_count = Plan.query.filter_by(is_active=True).count()
    return jsonify(code=0, msg="success", data={
        "users": users_count,
        "messages": messages_count,
        "unread_messages": unread,
        "exercises": exercises_count,
        "plans": plans_count,
    })


@admin_bp.route("/messages", methods=["GET"])
@require_admin
def get_messages(user):
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    # 最新留言排前面，管理员先处理新消息
    q = ContactMessage.query.order_by(ContactMessage.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return jsonify(code=0, msg="success", data={
        "items": [m.to_dict() for m in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@admin_bp.route("/messages/<int:msg_id>/read", methods=["PUT"])
@require_admin
def mark_read(user, msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify(code=0, msg="success", data=msg.to_dict())


@admin_bp.route("/users", methods=["GET"])
@require_admin
def get_users(user):
    q = User.query.order_by(User.id)
    items = q.all()
    data = [u.to_dict(exclude=["password_hash"]) for u in items]
    return jsonify(code=0, msg="success", data={"items": data, "total": len(data)})


@admin_bp.route("/exercises", methods=["GET"])
@require_admin
def get_exercises(user):
    items = Exercise.query.order_by(Exercise.id).all()
    return jsonify(code=0, msg="success", data={"items": [e.to_dict() for e in items], "total": len(items)})


@admin_bp.route("/plans", methods=["GET"])
@require_admin
def get_plans(user):
    items = Plan.query.order_by(Plan.id).all()
    return jsonify(code=0, msg="success", data={"items": [p.to_dict() for p in items], "total": len(items)})


@admin_bp.route("/plans/<int:plan_id>/toggle-status", methods=["PUT"])
@require_admin
def toggle_plan_status(user, plan_id):
    """计划上架 / 下架"""
    plan = Plan.query.get_or_404(plan_id)
    plan.is_active = not plan.is_active
    db.session.commit()
    return jsonify(code=0, msg="success", data=plan.to_dict())


@admin_bp.route("/plans", methods=["POST"])
@require_admin
def create_plan(user):
    """新增训练计划"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(code=400, msg="计划名称不能为空"), 400
    difficulty = data.get("difficulty", "intermediate")
    diff_map = {"beginner": "入门", "intermediate": "中级", "advanced": "高级"}
    plan = Plan(
        name=name,
        goal=(data.get("goal") or "muscle").strip(),
        badge=(data.get("badge") or "推荐").strip(),
        description=(data.get("description") or "").strip(),
        duration=(data.get("duration") or "").strip(),
        frequency=(data.get("frequency") or "").strip(),
        difficulty=difficulty,
        difficulty_label=diff_map.get(difficulty, "中级"),
        focus_tags=data.get("focus_tags", []),
        cover_url=(data.get("cover_url") or "").strip(),
        weekly_schedule=data.get("weekly_schedule", []),
        is_active=True,
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(code=0, msg="计划创建成功", data=plan.to_dict()), 201


@admin_bp.route("/plans/<int:plan_id>", methods=["PUT"])
@require_admin
def update_plan(user, plan_id):
    """编辑训练计划（动作管理同款：基础字段可改，难度联动显示名）"""
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json(silent=True) or {}
    for field in ["name", "goal", "badge", "description", "duration", "frequency", "cover_url"]:
        if field in data:
            val = data[field]
            if isinstance(val, str):
                val = val.strip()
            setattr(plan, field, val)
    if "difficulty" in data and data["difficulty"] in {"beginner", "intermediate", "advanced"}:
        plan.difficulty = data["difficulty"]
        plan.difficulty_label = {"beginner": "入门", "intermediate": "中级", "advanced": "高级"}[data["difficulty"]]
    db.session.commit()
    return jsonify(code=0, msg="计划更新成功", data=plan.to_dict())


@admin_bp.route("/body-metrics", methods=["GET"])
@require_admin
def get_all_metrics(user):
    items = BodyMetric.query.order_by(BodyMetric.id).all()
    return jsonify(code=0, msg="success", data={"items": [m.to_dict() for m in items], "total": len(items)})

@admin_bp.route("/exercises/<int:exercise_id>/toggle-status", methods=["PUT"])
@require_admin
def toggle_exercise_status(user, exercise_id):
    ex = Exercise.query.get_or_404(exercise_id)
    ex.is_active = not ex.is_active
    db.session.commit()
    return jsonify(code=0, msg="success", data=ex.to_dict())

@admin_bp.route("/exercises", methods=["POST"])
@require_admin
def create_exercise(user):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "").strip()
    if not name:
        return jsonify(code=400, msg="动作名称不能为空"), 400
    if not category:
        return jsonify(code=400, msg="请选择部位分类"), 400
    # Get category label
    cat = ExerciseCategory.query.filter_by(key=category).first()
    category_label = cat.label if cat else category
    difficulty = data.get("difficulty", "beginner")
    difficulty_map = {"beginner": "入门", "intermediate": "中级", "advanced": "高级"}
    difficulty_label = difficulty_map.get(difficulty, "入门")
    ex = Exercise(
        name=name,
        category=category,
        category_label=category_label,
        description=(data.get("description") or "").strip(),
        difficulty=difficulty,
        difficulty_label=difficulty_label,
        duration=(data.get("duration") or "").strip(),
        cover_url=(data.get("cover_url") or "").strip(),
        video_url=(data.get("video_url") or "").strip(),
        is_active=True,
    )
    db.session.add(ex)
    db.session.commit()
    return jsonify(code=0, msg="动作创建成功", data=ex.to_dict()), 201

@admin_bp.route("/exercises/<int:exercise_id>", methods=["PUT"])
@require_admin
def update_exercise(user, exercise_id):
    ex = Exercise.query.get_or_404(exercise_id)
    data = request.get_json(silent=True) or {}
    updatable = ["name", "category", "description", "difficulty", "duration", "cover_url", "video_url"]
    for field in updatable:
        if field in data:
            val = data[field]
            if isinstance(val, str):
                val = val.strip()
            setattr(ex, field, val)
            # Also update display labels if category or difficulty changed
            if field == "category":
                cat = ExerciseCategory.query.filter_by(key=val).first()
                if cat:
                    ex.category_label = cat.label
            if field == "difficulty":
                diff_map = {"beginner": "入门", "intermediate": "中级", "advanced": "高级"}
                ex.difficulty_label = diff_map.get(val, "入门")
    db.session.commit()
    return jsonify(code=0, msg="动作更新成功", data=ex.to_dict())

@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["PUT"])
@require_admin
def toggle_user_status(user, user_id):
    target = User.query.get_or_404(user_id)
    if target.is_admin:
        # 不允许通过后台互相禁用管理员，避免误操作把自己或他人锁死
        return jsonify(code=400, msg="不能操作管理员账号"), 400
    target.is_active = not target.is_active
    db.session.commit()
    return jsonify(code=0, msg="success", data=target.to_dict(exclude=["password_hash"]))
@admin_bp.route("/review-requests", methods=["GET"])
@require_admin
def get_review_requests(user):
    from models.profile_request import ProfileChangeRequest
    status_filter = request.args.get("status", "pending")
    page = max(request.args.get("page", 1, type=int), 1)
    page_size = min(max(request.args.get("page_size", 20, type=int), 1), 100)
    q = ProfileChangeRequest.query.filter_by(status=status_filter).order_by(ProfileChangeRequest.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    # 批量取用户，避免循环里逐条查询（N+1）
    user_ids = {item.user_id for item in items}
    users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}

    result = []
    for item in items:
        d = item.to_dict()
        u = users.get(item.user_id)
        d["user_nickname"] = u.nickname if u else ""
        d["user_email"] = u.email if u else ""
        result.append(d)
    return jsonify(code=0, msg="success", data={"items": result, "total": total, "page": page, "page_size": page_size})

@admin_bp.route("/review-requests/<int:rid>", methods=["GET"])
@require_admin
def get_review_detail(user, rid):
    from models.profile_request import ProfileChangeRequest
    req = ProfileChangeRequest.query.get_or_404(rid)
    d = req.to_dict()
    u = db.session.get(User, req.user_id)
    d["user_nickname"] = u.nickname if u else ""
    d["user_email"] = u.email if u else ""
    return jsonify(code=0, msg="success", data=d)

@admin_bp.route("/review-requests/<int:rid>/approve", methods=["PUT"])
@require_admin
def approve_review(user, rid):
    from models.profile_request import ProfileChangeRequest
    req = ProfileChangeRequest.query.get_or_404(rid)
    if req.status != "pending":
        return jsonify(code=400, msg="已处理"), 400
    target = db.session.get(User, req.user_id)
    if target:
        model_field = {"avatar": "avatar_url"}.get(req.field_name, req.field_name)
        setattr(target, model_field, req.new_value)
    req.status = "approved"
    db.session.commit()
    return jsonify(code=0, msg="已通过审核", data=req.to_dict())

@admin_bp.route("/review-requests/<int:rid>/reject", methods=["PUT"])
@require_admin
def reject_review(user, rid):
    from models.profile_request import ProfileChangeRequest
    req = ProfileChangeRequest.query.get_or_404(rid)
    if req.status != "pending":
        return jsonify(code=400, msg="已处理"), 400
    req.status = "rejected"
    db.session.commit()
    return jsonify(code=0, msg="已拒绝", data=req.to_dict())
