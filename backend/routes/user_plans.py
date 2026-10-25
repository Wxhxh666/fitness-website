from flask import jsonify, request
from models import db
from models.plan import Plan
from models.exercise import ExerciseCategory
from models.user_plan import UserPlan
from models.workout import WorkoutSession
from services import workout as workout_svc
from utils.auth import require_auth
from datetime import date

from . import user_plans_bp


@user_plans_bp.route("", methods=["GET"])
@require_auth
def get_my_plans(user):
    items = UserPlan.query.filter_by(user_id=user.id).order_by(UserPlan.id.desc()).all()
    return jsonify(code=0, msg="success", data={"items": [p.to_dict() for p in items]})


@user_plans_bp.route("", methods=["POST"])
@require_auth
def create_plan(user):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(code=400, msg="计划名称不能为空"), 400
    plan = UserPlan(user_id=user.id)
    plan.from_dict({
        "name": name,
        "goal": (data.get("goal") or "").strip(),
        "description": (data.get("description") or "").strip(),
        "duration": (data.get("duration") or "").strip(),
        "frequency": (data.get("frequency") or "").strip(),
        "difficulty": data.get("difficulty", "intermediate"),
        "difficulty_label": data.get("difficulty_label", "中级"),
        "focus_tags": data.get("focus_tags", []),
        "weekly_schedule": data.get("weekly_schedule", []),
    })
    db.session.add(plan)
    db.session.commit()
    return jsonify(code=0, msg="计划创建成功", data=plan.to_dict()), 201


@user_plans_bp.route("/<int:plan_id>", methods=["GET"])
@require_auth
def get_plan_detail(user, plan_id):
    plan = UserPlan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()
    return jsonify(code=0, msg="success", data=plan.to_dict())


@user_plans_bp.route("/<int:plan_id>", methods=["PUT"])
@require_auth
def update_plan(user, plan_id):
    plan = UserPlan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    updatable = ["name", "goal", "description", "duration", "frequency",
                 "difficulty", "difficulty_label", "focus_tags", "weekly_schedule"]
    for field in updatable:
        if field in data:
            setattr(plan, field, data[field])
    db.session.commit()
    return jsonify(code=0, msg="计划更新成功", data=plan.to_dict())


@user_plans_bp.route("/<int:plan_id>", methods=["DELETE"])
@require_auth
def delete_plan(user, plan_id):
    plan = UserPlan.query.filter_by(id=plan_id, user_id=user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    return jsonify(code=0, msg="计划已删除")


@user_plans_bp.route("/clone/<int:official_plan_id>", methods=["POST"])
@require_auth
def clone_plan(user, official_plan_id):
    official = Plan.query.get_or_404(official_plan_id)
    plan = UserPlan(user_id=user.id)
    plan.from_dict({
        "name": official.name + " (我的)",
        "goal": official.goal,
        "description": official.description,
        "duration": official.duration,
        "frequency": official.frequency,
        "difficulty": official.difficulty,
        "difficulty_label": official.difficulty_label,
        "focus_tags": official.focus_tags,
        "weekly_schedule": official.weekly_schedule,
        "source_plan_id": official.id,
    })
    db.session.add(plan)
    db.session.commit()
    return jsonify(code=0, msg="计划已克隆", data=plan.to_dict()), 201


# ---------- Training Logs ----------
# 说明：旧实现写 training_logs（一天一条、动作用 JSON 存），已于
# 2026-10 迁移到 workout_sessions / workout_sets（细化到组）。
# 这里保留原有 URL 作为「一键打卡」的轻量入口，内部写新的会话表，
# 详细到组的录入走 /api/workouts/*。

TRAINING_LOG_PLACEHOLDER = "（由训练打卡创建，可在运动记录中补充组数）"


@user_plans_bp.route("/training/log", methods=["POST"])
@require_auth
def log_training(user):
    data = request.get_json(silent=True) or {}
    log_date_str = data.get("log_date") or date.today().isoformat()
    log_date = _parse_date(log_date_str)

    plan_id = data.get("plan_id") or None
    focus = (data.get("focus") or "").strip()[:32]
    note = (data.get("note") or "").strip()

    existing = WorkoutSession.query.filter_by(
        user_id=user.id, session_date=log_date, plan_id=plan_id,
    ).first()
    if existing:
        existing.focus = focus or existing.focus
        if note:
            existing.note = note
    else:
        title = focus or "训练打卡"
        db.session.add(WorkoutSession(
            user_id=user.id,
            session_date=log_date,
            title=title[:64],
            focus=focus,
            plan_id=plan_id,
            note=note,
            total_sets=0, total_reps=0, total_volume=0.0,
        ))
    db.session.commit()
    return jsonify(code=0, msg="训练已记录")


def _parse_date(value):
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return date.today()


@user_plans_bp.route("/training/logs", methods=["GET"])
@require_auth
def get_training_logs(user):
    days = request.args.get("days", 30, type=int)
    plan_id = request.args.get("plan_id", type=int)
    from datetime import timedelta
    since = date.today() - timedelta(days=days)
    q = WorkoutSession.query.filter(
        WorkoutSession.user_id == user.id,
        WorkoutSession.session_date >= since,
    ).order_by(WorkoutSession.session_date.desc())
    if plan_id:
        q = q.filter_by(plan_id=plan_id)
    # 保持旧字段名 log_date，避免老前端读不到
    items = []
    for s in q.all():
        d = s.to_dict()
        d["log_date"] = d.pop("session_date", None)
        items.append(d)
    return jsonify(code=0, msg="success", data=items)


@user_plans_bp.route("/training/stats", methods=["GET"])
@require_auth
def get_training_stats(user):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    week_count = WorkoutSession.query.filter(
        WorkoutSession.user_id == user.id,
        WorkoutSession.session_date >= week_start,
    ).count()

    month_count = WorkoutSession.query.filter(
        WorkoutSession.user_id == user.id,
        WorkoutSession.session_date >= month_start,
    ).count()

    total_count = WorkoutSession.query.filter_by(user_id=user.id).count()

    latest = (WorkoutSession.query.filter_by(user_id=user.id)
              .order_by(WorkoutSession.session_date.desc()).first())

    return jsonify(code=0, msg="success", data={
        "week_count": week_count,
        "month_count": month_count,
        "total_count": total_count,
        "latest_log_date": latest.session_date.isoformat() if latest else None,
        "current_streak": workout_svc.current_streak(user.id, today),
    })
