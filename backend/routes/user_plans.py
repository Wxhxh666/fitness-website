from flask import Blueprint, jsonify, request
from models import db
from models.plan import Plan
from models.exercise import ExerciseCategory
from models.user_plan import UserPlan, TrainingLog
from utils.auth import require_auth
from datetime import date

user_plans_bp = Blueprint("user_plans", __name__)


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

@user_plans_bp.route("/training/log", methods=["POST"])
@require_auth
def log_training(user):
    data = request.get_json(silent=True) or {}
    log_date_str = data.get("log_date") or date.today().isoformat()
    try:
        log_date = date.fromisoformat(log_date_str)
    except:
        log_date = date.today()

    plan_id = data.get("plan_id", 0)
    is_official = data.get("is_official", False)

    existing = TrainingLog.query.filter_by(user_id=user.id, log_date=log_date).first()
    if existing:
        existing.plan_id = plan_id
        existing.is_official = is_official
        existing.focus = data.get("focus", existing.focus)
        existing.exercises = data.get("exercises", existing.exercises)
        existing.note = data.get("note", existing.note)
    else:
        log = TrainingLog(
            user_id=user.id, plan_id=plan_id,
            is_official=is_official, log_date=log_date,
            focus=data.get("focus", ""),
            exercises=data.get("exercises", []),
            note=(data.get("note") or "").strip(),
        )
        db.session.add(log)
    db.session.commit()
    return jsonify(code=0, msg="训练已记录")


@user_plans_bp.route("/training/logs", methods=["GET"])
@require_auth
def get_training_logs(user):
    days = request.args.get("days", 30, type=int)
    plan_id = request.args.get("plan_id", type=int)
    from datetime import timedelta
    since = date.today() - timedelta(days=days)
    q = TrainingLog.query.filter(
        TrainingLog.user_id == user.id,
        TrainingLog.log_date >= since,
    ).order_by(TrainingLog.log_date.desc())
    if plan_id:
        q = q.filter_by(plan_id=plan_id)
    items = q.all()
    return jsonify(code=0, msg="success", data=[t.to_dict() for t in items])


@user_plans_bp.route("/training/stats", methods=["GET"])
@require_auth
def get_training_stats(user):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    week_count = TrainingLog.query.filter(
        TrainingLog.user_id == user.id,
        TrainingLog.log_date >= week_start,
    ).count()

    month_count = TrainingLog.query.filter(
        TrainingLog.user_id == user.id,
        TrainingLog.log_date >= month_start,
    ).count()

    total_count = TrainingLog.query.filter_by(user_id=user.id).count()

    latest = TrainingLog.query.filter_by(user_id=user.id).order_by(TrainingLog.log_date.desc()).first()

    return jsonify(code=0, msg="success", data={
        "week_count": week_count,
        "month_count": month_count,
        "total_count": total_count,
        "latest_log_date": latest.log_date.isoformat() if latest else None,
        "current_streak": _calc_streak(user.id, today),
    })


def _calc_streak(user_id, today):
    from datetime import timedelta
    streak = 0
    d = today
    while True:
        log = TrainingLog.query.filter_by(user_id=user_id, log_date=d).first()
        if log:
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak
