# -*- coding: utf-8 -*-
"""成就勋章：把已有的训练 / 身材数据换算成可展示的成就。

设计取舍：
- **不落库**。所有成就都能从原始数据推导出来（第 N 次训练、累计容量、最长连续天数……），
  存一张 achievement 表反而要处理"删了记录成就还算不算"的一致性难题。
  纯计算的开销是几个聚合查询，代价可以忽略。
- 只统计训练与身材数据，不涉及饮食模块。
"""

from datetime import date

from sqlalchemy import func

from models import db
from models.body_record import BodyRecord, BodyGoal
from models.workout import WorkoutSession, WorkoutSet
from services.workout import longest_streak

# category: training 训练 / body 身材 / streak 坚持
ACHIEVEMENTS = [
    # ---------- 训练 ----------
    {"key": "first_workout", "name": "启程", "desc": "完成第一次训练记录", "category": "training",
     "tier": "bronze", "icon": "Flag", "metric": "sessions", "target": 1, "unit": "次"},
    {"key": "workout_10", "name": "渐入佳境", "desc": "累计完成 10 次训练", "category": "training",
     "tier": "silver", "icon": "Timer", "metric": "sessions", "target": 10, "unit": "次"},
    {"key": "workout_50", "name": "铁打的人", "desc": "累计完成 50 次训练", "category": "training",
     "tier": "gold", "icon": "Medal", "metric": "sessions", "target": 50, "unit": "次"},
    {"key": "workout_100", "name": "百炼成钢", "desc": "累计完成 100 次训练", "category": "training",
     "tier": "gold", "icon": "Trophy", "metric": "sessions", "target": 100, "unit": "次"},
    {"key": "volume_5t", "name": "单场五吨", "desc": "单次训练总容量达到 5000 kg", "category": "training",
     "tier": "silver", "icon": "Histogram", "metric": "max_volume", "target": 5000, "unit": "kg"},
    {"key": "volume_10t", "name": "单场十吨", "desc": "单次训练总容量达到 10000 kg", "category": "training",
     "tier": "gold", "icon": "Lightning", "metric": "max_volume", "target": 10000, "unit": "kg"},
    {"key": "total_50t", "name": "五十吨俱乐部", "desc": "累计训练容量达到 50000 kg", "category": "training",
     "tier": "gold", "icon": "TrophyBase", "metric": "total_volume", "target": 50000, "unit": "kg"},
    {"key": "exercise_5", "name": "动作探索者", "desc": "练过 5 个不同动作", "category": "training",
     "tier": "bronze", "icon": "Compass", "metric": "exercise_kinds", "target": 5, "unit": "个"},
    {"key": "exercise_20", "name": "动作百科", "desc": "练过 20 个不同动作", "category": "training",
     "tier": "silver", "icon": "Notebook", "metric": "exercise_kinds", "target": 20, "unit": "个"},
    {"key": "minutes_600", "name": "十小时", "desc": "累计训练时长达到 600 分钟", "category": "training",
     "tier": "silver", "icon": "Clock", "metric": "total_minutes", "target": 600, "unit": "分钟"},

    # ---------- 坚持 ----------
    {"key": "streak_3", "name": "三日不辍", "desc": "连续训练 3 天", "category": "streak",
     "tier": "bronze", "icon": "Sunny", "metric": "longest_streak", "target": 3, "unit": "天"},
    {"key": "streak_7", "name": "一周不断", "desc": "连续训练 7 天", "category": "streak",
     "tier": "silver", "icon": "Sunrise", "metric": "longest_streak", "target": 7, "unit": "天"},
    {"key": "streak_30", "name": "月度铁人", "desc": "连续训练 30 天", "category": "streak",
     "tier": "gold", "icon": "Medal", "metric": "longest_streak", "target": 30, "unit": "天"},

    # ---------- 身材 ----------
    {"key": "first_record", "name": "初次记录", "desc": "保存第一条身材数据", "category": "body",
     "tier": "bronze", "icon": "Crop", "metric": "body_records", "target": 1, "unit": "条"},
    {"key": "record_10", "name": "有据可查", "desc": "累计 10 条身材记录", "category": "body",
     "tier": "silver", "icon": "Files", "metric": "body_records", "target": 10, "unit": "条"},
    {"key": "record_30", "name": "数据控", "desc": "累计 30 条身材记录", "category": "body",
     "tier": "gold", "icon": "DataAnalysis", "metric": "body_records", "target": 30, "unit": "条"},
    {"key": "goal_set", "name": "有的放矢", "desc": "设定一个身材目标", "category": "body",
     "tier": "bronze", "icon": "Aim", "metric": "goal_set", "target": 1, "unit": "个"},
    {"key": "goal_reached", "name": "说到做到", "desc": "达成设定的身材目标", "category": "body",
     "tier": "gold", "icon": "CircleCheck", "metric": "goal_reached", "target": 1, "unit": "项"},
]

CATEGORY_LABELS = {"training": "训练", "streak": "坚持", "body": "身材"}
TIER_ORDER = {"gold": 3, "silver": 2, "bronze": 1}


def _collect_stats(user_id):
    """一次查询拿齐所有需要的聚合值"""
    sessions, total_volume, max_volume, total_minutes = (
        db.session.query(
            func.count(WorkoutSession.id),
            func.coalesce(func.sum(WorkoutSession.total_volume), 0),
            func.coalesce(func.max(WorkoutSession.total_volume), 0),
            func.coalesce(func.sum(WorkoutSession.duration_min), 0),
        )
        .filter(WorkoutSession.user_id == user_id)
        .one()
    )
    exercise_kinds = (
        db.session.query(func.count(func.distinct(WorkoutSet.exercise_name)))
        .filter(WorkoutSet.user_id == user_id)
        .scalar() or 0
    )
    body_records = BodyRecord.query.filter_by(user_id=user_id).count()
    goal = BodyGoal.query.filter_by(user_id=user_id).order_by(BodyGoal.id.desc()).first()

    return {
        "sessions": int(sessions or 0),
        "total_volume": round(float(total_volume or 0), 1),
        "max_volume": round(float(max_volume or 0), 1),
        "total_minutes": int(total_minutes or 0),
        "exercise_kinds": int(exercise_kinds or 0),
        "body_records": int(body_records or 0),
        "goal_set": 1 if goal else 0,
        "goal_reached": 1 if _goal_reached(user_id, goal) else 0,
        "longest_streak": longest_streak(user_id),
    }


def _goal_reached(user_id, goal):
    """目标是否达成：任一已设目标与最近记录足够接近即算

    容差取「0.3 或目标值的 0.5%」中的较大者，避免 60.0 vs 59.95 这种浮点误差卡住成就。
    """
    if not goal:
        return False
    latest = (BodyRecord.query
              .filter_by(user_id=user_id)
              .order_by(BodyRecord.record_date.desc(), BodyRecord.id.desc())
              .first())
    if not latest:
        return False

    checks = [
        (goal.target_weight, latest.weight_kg),
        (goal.target_bmi, latest.bmi),
        (goal.target_body_fat, latest.body_fat),
    ]
    for target, actual in checks:
        if target is None or actual is None:
            continue
        tol = max(0.3, abs(float(target)) * 0.005)
        if abs(float(actual) - float(target)) <= tol:
            return True
    return False


def achievement_list(user_id):
    """返回全部成就（含未解锁项的进度），按 已解锁 → 等级 → 分类 排序"""
    stats = _collect_stats(user_id)
    items = []
    for a in ACHIEVEMENTS:
        current = stats.get(a["metric"], 0) or 0
        target = a["target"]
        unlocked = current >= target
        items.append({
            "key": a["key"],
            "name": a["name"],
            "desc": a["desc"],
            "category": a["category"],
            "category_label": CATEGORY_LABELS.get(a["category"], a["category"]),
            "tier": a["tier"],
            "icon": a["icon"],
            "metric": a["metric"],
            "unit": a["unit"],
            "current": round(float(current), 1),
            "target": target,
            "progress": round(min(1.0, current / target), 3) if target else 0.0,
            "unlocked": unlocked,
        })

    # 已解锁的按等级从高到低（金牌在最前）；未解锁的按进度从高到低，
    # 让用户先看到"再练两次就能拿到"的那个，而不是排第一的 30 天金牌。
    # 进度并列（新用户全是 0）时按等级升序，从最容易的铜牌开始推荐。
    items.sort(key=lambda x: (
        0 if x["unlocked"] else 1,
        -TIER_ORDER.get(x["tier"], 0) if x["unlocked"] else 0,
        -x["progress"],
        TIER_ORDER.get(x["tier"], 0),
        x["key"],
    ))

    unlocked = [i for i in items if i["unlocked"]]
    by_category = {}
    for i in items:
        c = by_category.setdefault(i["category"], {"total": 0, "unlocked": 0})
        c["total"] += 1
        if i["unlocked"]:
            c["unlocked"] += 1

    return {
        "items": items,
        "summary": {
            "unlocked": len(unlocked),
            "total": len(items),
            "completion": round(len(unlocked) / len(items), 3) if items else 0.0,
            "gold": sum(1 for i in unlocked if i["tier"] == "gold"),
            "silver": sum(1 for i in unlocked if i["tier"] == "silver"),
            "bronze": sum(1 for i in unlocked if i["tier"] == "bronze"),
            "by_category": by_category,
            "next": next((i for i in items if not i["unlocked"]), None),
        },
        "stats": stats,
    }
