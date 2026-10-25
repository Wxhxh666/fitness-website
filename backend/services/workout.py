# -*- coding: utf-8 -*-
"""运动记录领域逻辑：汇总重算、PR 维护、连续天数、趋势序列。"""

from datetime import date, datetime, timedelta

from sqlalchemy import func

from models import db
from models.workout import (
    WorkoutSession, WorkoutSet, PersonalRecord,
    PR_E1RM, PR_MAX_WEIGHT, PR_MAX_REPS, PR_MAX_VOLUME,
)

RECORD_TYPES = (PR_E1RM, PR_MAX_WEIGHT, PR_MAX_REPS, PR_MAX_VOLUME)


# ---------------------------------------------------------------- 会话汇总

def recalc_session(session):
    """按组重算 session 上的冗余汇总字段（热身组计入组数，但不计入容量）"""
    rows = WorkoutSet.query.filter_by(session_id=session.id).all()
    work = [r for r in rows if not r.is_warmup]
    session.total_sets = len(rows)
    session.total_reps = sum(r.reps or 0 for r in work)
    session.total_volume = round(sum((r.weight_kg or 0) * (r.reps or 0) for r in work), 1)
    return session


def session_brief(session):
    d = session.to_dict()
    d["set_count"] = session.total_sets or 0
    return d


def grouped_sets(session):
    """按动作分组，组内按 set_index 排序，前端可直接渲染"""
    rows = (WorkoutSet.query
            .filter_by(session_id=session.id)
            .order_by(WorkoutSet.id.asc())
            .all())
    groups = {}
    order = []
    for r in rows:
        if r.exercise_name not in groups:
            groups[r.exercise_name] = {
                "exercise_name": r.exercise_name,
                "exercise_id": r.exercise_id,
                "sets": [],
                "total_volume": 0.0,
                "best_e1rm": 0.0,
            }
            order.append(r.exercise_name)
        g = groups[r.exercise_name]
        g["sets"].append(r.to_dict())
        if not r.is_warmup:
            g["total_volume"] = round(g["total_volume"] + (r.weight_kg or 0) * (r.reps or 0), 1)
            g["best_e1rm"] = max(g["best_e1rm"], r.e1rm)
    return [groups[k] for k in order]


# ---------------------------------------------------------------- PR 维护

def _best_of_sets(sets):
    """从一组 WorkoutSet 里算出四项纪录的最佳值"""
    work = [s for s in sets if not s.is_warmup]
    best = {k: {"value": 0.0, "weight_kg": 0.0, "reps": 0, "set": None} for k in RECORD_TYPES}
    for s in work:
        cand = {
            PR_E1RM: (s.e1rm, s.weight_kg or 0, s.reps or 0),
            PR_MAX_WEIGHT: (s.weight_kg or 0, s.weight_kg or 0, s.reps or 0),
            PR_MAX_REPS: (s.reps or 0, s.weight_kg or 0, s.reps or 0),
            PR_MAX_VOLUME: ((s.weight_kg or 0) * (s.reps or 0), s.weight_kg or 0, s.reps or 0),
        }
        for k, (val, w, r) in cand.items():
            if val and val > best[k]["value"]:
                best[k] = {"value": round(val, 1), "weight_kg": w, "reps": r, "set": s}
    return best


def recompute_prs(user_id, exercise_name):
    """
    按「该用户该动作的全部历史组」重算四项 PR。
    之所以全量重算而不是增量比较：改一组、删一组都可能让旧纪录失效，
    全量重算逻辑简单且绝不会留下脏纪录（单动作组数很少，成本可忽略）。
    返回本次刷新后**创新高**的纪录列表，用于前端弹「新纪录」提示。
    """
    sets = (WorkoutSet.query
            .filter_by(user_id=user_id, exercise_name=exercise_name)
            .all())
    best = _best_of_sets(sets)

    existing = {p.record_type: p for p in
                PersonalRecord.query.filter_by(user_id=user_id, exercise_name=exercise_name).all()}
    raised = []
    for rtype, info in best.items():
        old = existing.get(rtype)
        old_value = old.value if old else 0.0
        if info["value"] <= 0:
            if old:
                db.session.delete(old)
            continue
        if old:
            old.value = info["value"]
            old.weight_kg = info["weight_kg"]
            old.reps = info["reps"]
            if info["set"] is not None:
                old.session_id = info["set"].session_id
                old.set_id = info["set"].id
                old.exercise_id = info["set"].exercise_id
                old.achieved_at = _set_datetime(info["set"])
            if info["value"] > old_value + 1e-9:
                raised.append({**old.to_dict(), "previous_value": old_value})
        else:
            s = info["set"]
            pr = PersonalRecord(
                user_id=user_id,
                exercise_name=exercise_name,
                exercise_id=(s.exercise_id if s else None),
                record_type=rtype,
                value=info["value"],
                weight_kg=info["weight_kg"],
                reps=info["reps"],
                session_id=(s.session_id if s else None),
                set_id=(s.id if s else None),
                achieved_at=_set_datetime(s) if s else None,
            )
            db.session.add(pr)
            raised.append({**pr.to_dict(), "previous_value": 0.0})
    return raised


def _set_datetime(s):
    """组的达成时间：取所属训练的 session_date，没有就用创建时间"""
    if s is None:
        return None
    sess = WorkoutSession.query.get(s.session_id) if s.session_id else None
    if sess and sess.session_date:
        return datetime.combine(sess.session_date, datetime.min.time())
    return s.created_at


# ---------------------------------------------------------------- 统计

def _distinct_dates(user_id, since=None):
    q = db.session.query(WorkoutSession.session_date).filter(WorkoutSession.user_id == user_id)
    if since:
        q = q.filter(WorkoutSession.session_date >= since)
    return sorted({row[0] for row in q.all()})


def current_streak(user_id, today=None):
    """
    连续训练天数。今天还没练不算断——从昨天往前数，
    避免用户早上打开 App 就看到连续天数归零。
    """
    today = today or date.today()
    dates = set(_distinct_dates(user_id))
    cursor = today if today in dates else today - timedelta(days=1)
    streak = 0
    while cursor in dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def longest_streak(user_id):
    dates = _distinct_dates(user_id)
    best = cur = 0
    prev = None
    for d in dates:
        cur = cur + 1 if prev and (d - prev).days == 1 else 1
        best = max(best, cur)
        prev = d
    return best


def range_stats(user_id, start, end=None):
    """区间统计：训练次数 / 组数 / 次数 / 容量 / 时长"""
    end = end or date.today()
    row = (db.session.query(
        func.count(WorkoutSession.id),
        func.coalesce(func.sum(WorkoutSession.total_sets), 0),
        func.coalesce(func.sum(WorkoutSession.total_reps), 0),
        func.coalesce(func.sum(WorkoutSession.total_volume), 0),
        func.coalesce(func.sum(WorkoutSession.duration_min), 0),
    )
        .filter(WorkoutSession.user_id == user_id,
                WorkoutSession.session_date >= start,
                WorkoutSession.session_date <= end)
        .one())
    sessions, sets, reps, volume, minutes = row
    return {
        "sessions": int(sessions or 0),
        "sets": int(sets or 0),
        "reps": int(reps or 0),
        "volume": round(float(volume or 0), 1),
        "minutes": int(minutes or 0),
        "avg_duration": round(float(minutes or 0) / sessions, 1) if sessions else 0,
    }


def overview(user_id, today=None):
    """首页/训练页顶部用的一组数字"""
    today = today or date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    return {
        "today": range_stats(user_id, today, today),
        "week": range_stats(user_id, week_start, today),
        "month": range_stats(user_id, month_start, today),
        "total": range_stats(user_id, date(1970, 1, 1), today),
        "current_streak": current_streak(user_id, today),
        "longest_streak": longest_streak(user_id),
        "week_start": week_start.isoformat(),
    }


def weekly_volume_series(user_id, weeks=12, today=None):
    """最近 N 周的训练容量（按自然周聚合，用于柱状图）"""
    today = today or date.today()
    this_monday = today - timedelta(days=today.weekday())
    start = this_monday - timedelta(weeks=weeks - 1)
    rows = (db.session.query(WorkoutSession.session_date,
                             WorkoutSession.total_volume,
                             WorkoutSession.total_sets)
            .filter(WorkoutSession.user_id == user_id,
                    WorkoutSession.session_date >= start)
            .all())
    buckets = {}
    for offset in range(weeks):
        ws = start + timedelta(weeks=offset)
        buckets[ws] = {"week_start": ws.isoformat(), "volume": 0.0, "sets": 0, "sessions": 0}
    for d, volume, sets in rows:
        ws = d - timedelta(days=d.weekday())
        if ws in buckets:
            buckets[ws]["volume"] = round(buckets[ws]["volume"] + float(volume or 0), 1)
            buckets[ws]["sets"] += int(sets or 0)
            buckets[ws]["sessions"] += 1
    return [buckets[start + timedelta(weeks=i)] for i in range(weeks)]


def calendar_days(user_id, year, month):
    """月历热力图：返回 {日期: 训练信息}"""
    from calendar import monthrange
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    rows = (WorkoutSession.query
            .filter(WorkoutSession.user_id == user_id,
                    WorkoutSession.session_date >= first,
                    WorkoutSession.session_date <= last)
            .all())
    out = {}
    for s in rows:
        key = s.session_date.isoformat()
        item = out.setdefault(key, {"date": key, "sessions": 0, "volume": 0.0, "sets": 0, "titles": []})
        item["sessions"] += 1
        item["volume"] = round(item["volume"] + float(s.total_volume or 0), 1)
        item["sets"] += int(s.total_sets or 0)
        if s.title:
            item["titles"].append(s.title)
    return sorted(out.values(), key=lambda x: x["date"])


def exercise_history(user_id, exercise_name, limit=40):
    """某动作的历史曲线：每次训练一条（最佳 e1RM / 最大重量 / 容量）"""
    dates = (db.session.query(WorkoutSession.id, WorkoutSession.session_date)
             .filter(WorkoutSession.user_id == user_id)
             .order_by(WorkoutSession.session_date.desc())
             .limit(limit)
             .all())
    ids = [i for i, _ in dates]
    if not ids:
        return []
    rows = (WorkoutSet.query
            .filter(WorkoutSet.user_id == user_id,
                    WorkoutSet.exercise_name == exercise_name,
                    WorkoutSet.session_id.in_(ids))
            .all())
    by_session = {}
    for r in rows:
        by_session.setdefault(r.session_id, []).append(r)
    out = []
    for sid, d in dates:
        sets = by_session.get(sid)
        if not sets:
            continue
        work = [s for s in sets if not s.is_warmup]
        out.append({
            "session_id": sid,
            "date": d.isoformat(),
            "sets": len(sets),
            "reps": sum(s.reps or 0 for s in work),
            "volume": round(sum((s.weight_kg or 0) * (s.reps or 0) for s in work), 1),
            "best_e1rm": max([s.e1rm for s in work], default=0.0),
            "max_weight": max([(s.weight_kg or 0) for s in work], default=0.0),
        })
    return list(reversed(out))


def my_exercises(user_id):
    """用户练过的动作 + 最近一次的重量/次数，用于快速添加和「上次记录」提示"""
    names = [r[0] for r in
             db.session.query(WorkoutSet.exercise_name)
             .filter(WorkoutSet.user_id == user_id)
             .group_by(WorkoutSet.exercise_name)
             .order_by(func.count(WorkoutSet.id).desc())
             .all()]
    out = []
    for name in names:
        last = (WorkoutSet.query
                .filter_by(user_id=user_id, exercise_name=name)
                .order_by(WorkoutSet.id.desc())
                .first())
        out.append({
            "exercise_name": name,
            "last_weight_kg": last.weight_kg if last else 0,
            "last_reps": last.reps if last else 0,
            "last_date": _last_date(user_id, name),
            "sessions": (db.session.query(func.count(func.distinct(WorkoutSet.session_id)))
                         .filter(WorkoutSet.user_id == user_id,
                                 WorkoutSet.exercise_name == name).scalar() or 0),
        })
    return out


def _last_date(user_id, exercise_name):
    row = (db.session.query(WorkoutSession.session_date)
           .join(WorkoutSet, WorkoutSet.session_id == WorkoutSession.id)
           .filter(WorkoutSet.user_id == user_id, WorkoutSet.exercise_name == exercise_name)
           .order_by(WorkoutSession.session_date.desc())
           .first())
    return row[0].isoformat() if row else None
