# -*- coding: utf-8 -*-
"""
运动记录接口。

约定：
- 所有接口都需要登录，且任何按 id 的操作都带 user_id 条件，查不到就是 404（不区分「不存在」和「不是你的」）。
- 写入组记录后统一重算 session 汇总与对应动作的 PR，接口直接返回最新统计，前端不用再拉一次。
"""
from datetime import date, datetime

from flask import jsonify, request

from models import db
from models.workout import WorkoutSession, WorkoutSet, PersonalRecord
from services import workout as svc
from utils.auth import require_auth

from . import workouts_bp

MAX_WEIGHT = 1000.0
MAX_REPS = 1000


def _parse_date(value, default=None):
    if not value:
        return default or date.today()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return default or date.today()


def _num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _get_session(user, session_id):
    return WorkoutSession.query.filter_by(id=session_id, user_id=user.id).first()


def _clean_set_payload(data):
    """把前端传的组数据规范化并做边界校验，返回 (payload, error)"""
    name = (data.get("exercise_name") or "").strip()
    if not name:
        return None, "请填写动作名称"
    if len(name) > 64:
        return None, "动作名称过长"

    weight = _num(data.get("weight_kg"), 0.0)
    reps = _int(data.get("reps"), 0)
    if weight < 0 or weight > MAX_WEIGHT:
        return None, f"重量需在 0-{int(MAX_WEIGHT)} kg 之间"
    if reps < 0 or reps > MAX_REPS:
        return None, f"次数需在 0-{MAX_REPS} 之间"
    if weight <= 0 and reps <= 0:
        return None, "重量和次数不能同时为 0"

    rpe = data.get("rpe")
    if rpe is not None and str(rpe) != "":
        rpe = _num(rpe)
        if rpe < 1 or rpe > 10:
            return None, "RPE 需在 1-10 之间"
    else:
        rpe = None

    return {
        "exercise_name": name,
        "exercise_id": data.get("exercise_id") or None,
        "weight_kg": round(weight, 1),
        "reps": reps,
        "rpe": rpe,
        "is_warmup": bool(data.get("is_warmup", False)),
        "rest_sec": _int(data["rest_sec"]) if data.get("rest_sec") not in (None, "") else None,
        "note": (data.get("note") or "")[:128],
    }, None


# ---------------------------------------------------------------- 会话

@workouts_bp.route("", methods=["GET"])
@require_auth
def list_sessions(user):
    days = request.args.get("days", type=int)
    limit = min(request.args.get("limit", 30, type=int), 200)
    offset = max(request.args.get("offset", 0, type=int), 0)

    q = WorkoutSession.query.filter_by(user_id=user.id)
    if days:
        from datetime import timedelta
        q = q.filter(WorkoutSession.session_date >= date.today() - timedelta(days=days))
    total = q.count()
    rows = (q.order_by(WorkoutSession.session_date.desc(), WorkoutSession.id.desc())
            .offset(offset).limit(limit).all())
    return jsonify(code=0, msg="success", data={
        "items": [svc.session_brief(s) for s in rows],
        "total": total,
        "has_more": offset + len(rows) < total,
    })


@workouts_bp.route("", methods=["POST"])
@require_auth
def create_session(user):
    data = request.get_json(silent=True) or {}
    session = WorkoutSession(
        user_id=user.id,
        session_date=_parse_date(data.get("session_date")),
        title=(data.get("title") or "").strip()[:64],
        focus=(data.get("focus") or "").strip()[:32],
        plan_id=data.get("plan_id") or None,
        note=(data.get("note") or "").strip(),
        duration_min=max(_int(data.get("duration_min"), 0), 0),
        feeling=_int(data["feeling"]) if data.get("feeling") not in (None, "") else None,
        total_sets=0, total_reps=0, total_volume=0.0,
    )
    db.session.add(session)
    db.session.commit()
    return jsonify(code=0, msg="训练已开始", data=svc.session_brief(session)), 201


@workouts_bp.route("/<int:session_id>", methods=["GET"])
@require_auth
def get_session(user, session_id):
    session = _get_session(user, session_id)
    if not session:
        return jsonify(code=404, msg="训练记录不存在"), 404
    d = session.to_dict()
    d["groups"] = svc.grouped_sets(session)
    return jsonify(code=0, msg="success", data=d)


@workouts_bp.route("/<int:session_id>", methods=["PUT"])
@require_auth
def update_session(user, session_id):
    session = _get_session(user, session_id)
    if not session:
        return jsonify(code=404, msg="训练记录不存在"), 404
    data = request.get_json(silent=True) or {}
    if "session_date" in data:
        session.session_date = _parse_date(data.get("session_date"), session.session_date)
    for field in ("title", "focus", "note"):
        if field in data:
            setattr(session, field, (data.get(field) or "").strip())
    if "plan_id" in data:
        session.plan_id = data.get("plan_id") or None
    if "duration_min" in data:
        session.duration_min = max(_int(data.get("duration_min"), 0), 0)
    if "feeling" in data:
        session.feeling = _int(data["feeling"]) if data.get("feeling") not in (None, "") else None
    db.session.commit()
    return jsonify(code=0, msg="已更新", data=svc.session_brief(session))


@workouts_bp.route("/<int:session_id>", methods=["DELETE"])
@require_auth
def delete_session(user, session_id):
    session = _get_session(user, session_id)
    if not session:
        return jsonify(code=404, msg="训练记录不存在"), 404
    names = {r.exercise_name for r in WorkoutSet.query.filter_by(session_id=session.id).all()}
    WorkoutSet.query.filter_by(session_id=session.id).delete(synchronize_session=False)
    db.session.delete(session)
    db.session.flush()
    # 删完这次训练后，相关动作的 PR 可能失效，需要重算
    for name in names:
        svc.recompute_prs(user.id, name)
    db.session.commit()
    return jsonify(code=0, msg="已删除")


# ---------------------------------------------------------------- 组

@workouts_bp.route("/<int:session_id>/sets", methods=["POST"])
@require_auth
def add_sets(user, session_id):
    session = _get_session(user, session_id)
    if not session:
        return jsonify(code=404, msg="训练记录不存在"), 404

    data = request.get_json(silent=True) or {}
    raw_sets = data.get("sets") if isinstance(data.get("sets"), list) else [data]
    if not raw_sets:
        return jsonify(code=400, msg="请至少提供一组数据"), 400

    payloads = []
    for raw in raw_sets:
        payload, err = _clean_set_payload(raw or {})
        if err:
            return jsonify(code=400, msg=err), 400
        payloads.append(payload)

    created = []
    touched = set()
    for payload in payloads:
        same = WorkoutSet.query.filter_by(session_id=session.id,
                                          exercise_name=payload["exercise_name"]).count()
        s = WorkoutSet(session_id=session.id, user_id=user.id,
                       set_index=same + 1, **payload)
        db.session.add(s)
        created.append(s)
        touched.add(payload["exercise_name"])
    db.session.flush()

    raised = []
    for name in touched:
        raised.extend(svc.recompute_prs(user.id, name))
    svc.recalc_session(session)
    db.session.commit()

    return jsonify(code=0, msg="已记录", data={
        "sets": [s.to_dict() for s in created],
        "session": svc.session_brief(session),
        "records": raised,
    }), 201


@workouts_bp.route("/<int:session_id>/sets/<int:set_id>", methods=["PUT"])
@require_auth
def update_set(user, session_id, set_id):
    s = WorkoutSet.query.filter_by(id=set_id, session_id=session_id, user_id=user.id).first()
    session = _get_session(user, session_id)
    if not s or not session:
        return jsonify(code=404, msg="组记录不存在"), 404

    data = request.get_json(silent=True) or {}
    merged = {
        "exercise_name": data.get("exercise_name", s.exercise_name),
        "exercise_id": data.get("exercise_id", s.exercise_id),
        "weight_kg": data.get("weight_kg", s.weight_kg),
        "reps": data.get("reps", s.reps),
        "rpe": data.get("rpe", s.rpe),
        "is_warmup": data.get("is_warmup", s.is_warmup),
        "rest_sec": data.get("rest_sec", s.rest_sec),
        "note": data.get("note", s.note),
    }
    payload, err = _clean_set_payload(merged)
    if err:
        return jsonify(code=400, msg=err), 400

    old_name = s.exercise_name
    for k, v in payload.items():
        setattr(s, k, v)
    db.session.flush()

    for name in {old_name, s.exercise_name}:
        svc.recompute_prs(user.id, name)
    svc.recalc_session(session)
    db.session.commit()
    return jsonify(code=0, msg="已更新", data={"set": s.to_dict(), "session": svc.session_brief(session)})


@workouts_bp.route("/<int:session_id>/sets/<int:set_id>", methods=["DELETE"])
@require_auth
def delete_set(user, session_id, set_id):
    s = WorkoutSet.query.filter_by(id=set_id, session_id=session_id, user_id=user.id).first()
    session = _get_session(user, session_id)
    if not s or not session:
        return jsonify(code=404, msg="组记录不存在"), 404
    name = s.exercise_name
    db.session.delete(s)
    db.session.flush()
    svc.recompute_prs(user.id, name)
    svc.recalc_session(session)
    db.session.commit()
    return jsonify(code=0, msg="已删除", data={"session": svc.session_brief(session)})


# ---------------------------------------------------------------- 统计与参考数据

@workouts_bp.route("/overview", methods=["GET"])
@require_auth
def overview(user):
    return jsonify(code=0, msg="success", data=svc.overview(user.id))


@workouts_bp.route("/volume-series", methods=["GET"])
@require_auth
def volume_series(user):
    weeks = min(max(request.args.get("weeks", 12, type=int), 4), 52)
    return jsonify(code=0, msg="success", data={"items": svc.weekly_volume_series(user.id, weeks)})


@workouts_bp.route("/calendar", methods=["GET"])
@require_auth
def calendar(user):
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    try:
        year, mon = [int(x) for x in month.split("-")[:2]]
    except (ValueError, TypeError):
        year, mon = date.today().year, date.today().month
    return jsonify(code=0, msg="success", data={
        "month": f"{year:04d}-{mon:02d}",
        "days": svc.calendar_days(user.id, year, mon),
    })


@workouts_bp.route("/prs", methods=["GET"])
@require_auth
def prs(user):
    rows = (PersonalRecord.query
            .filter_by(user_id=user.id)
            .order_by(PersonalRecord.achieved_at.is_(None), PersonalRecord.achieved_at.desc(),
                      PersonalRecord.id.desc())
            .all())
    by_type = {}
    for r in rows:
        by_type.setdefault(r.exercise_name, {})[r.record_type] = r.to_dict()
    items = []
    for name, recs in by_type.items():
        items.append({
            "exercise_name": name,
            "e1rm": recs.get("e1rm"),
            "max_weight": recs.get("max_weight"),
            "max_reps": recs.get("max_reps"),
            "max_volume": recs.get("max_volume"),
        })
    items.sort(key=lambda x: (x["e1rm"] or {}).get("value", 0), reverse=True)
    return jsonify(code=0, msg="success", data={"items": items})


@workouts_bp.route("/exercises", methods=["GET"])
@require_auth
def my_exercises(user):
    return jsonify(code=0, msg="success", data={"items": svc.my_exercises(user.id)})


@workouts_bp.route("/exercises/<path:name>/history", methods=["GET"])
@require_auth
def exercise_history(user, name):
    limit = min(max(request.args.get("limit", 30, type=int), 2), 100)
    return jsonify(code=0, msg="success", data={
        "exercise_name": name,
        "items": svc.exercise_history(user.id, name, limit),
    })
