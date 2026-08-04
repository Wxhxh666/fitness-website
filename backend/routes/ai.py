"""AI 饮食方案：DeepSeek 调用封装 + 方案存档"""
import json
import re
from datetime import date, datetime, timedelta

import requests
from flask import current_app, jsonify, request

from . import ai_bp
from models import db
from models.diet_plan import DietPlan
from models.diet_log import DietLog
from models.body_record import BodyRecord
from routes.body_metrics import compute_metrics, ACTIVITY_LABELS, GENDER_LABELS


TARGET_LABELS = {
    "fatloss": "减脂",
    "muscle": "增肌",
    "maintain": "维持体重",
}

TARGET_REVERSE = {v: k for k, v in TARGET_LABELS.items()}


DIET_PROMPT_TEMPLATE = """你是专业健身营养师，根据以下用户身体数据输出科学饮食方案，分模块清晰，语言简洁适配健身人群：
【用户基础数据】
身高：{height}cm，体重：{weight}kg，BMI：{bmi}，体脂率：{body_fat}，性别：{sex}，年龄：{age}
每日基础代谢BMR：{bmr}，每日总消耗TDEE：{tdee}
健身目标：{target}（减脂/增肌/维持体重）
每周运动强度：{sport_level}
饮食限制&偏好：{diet_limit}
就餐条件：{eat_scene}

输出要求：
1. 每日推荐总热量、蛋白质/碳水/脂肪三大营养素克数分配；
2. 一日三餐+可选加餐完整食谱（标注每份食材重量、热量）；
3. 饮水建议、饮食习惯禁忌；
4. 适配用户忌口，食谱全部避开过敏食材；
5. 简短健身饮食小贴士（结合用户BMI/体脂情况）；
6. 格式分段清晰，不要复杂markdown，适配网页展示。
"""

def normalize_target(target):
    if not target:
        return "fatloss", TARGET_LABELS["fatloss"]
    t = str(target).strip().lower()
    if t in TARGET_LABELS:
        return t, TARGET_LABELS[t]
    if t in TARGET_REVERSE:
        return TARGET_REVERSE[t], t
    if "增肌" in t:
        return "muscle", "增肌"
    if "维持" in t or "保持" in t:
        return "maintain", "维持体重"
    return "fatloss", "减脂"


def build_diet_prompt(data, user_message=""):
    """按内置模板构造 DeepSeek Prompt（含 JSON 输出要求）"""
    payload = dict(data)
    prompt = DIET_PROMPT_TEMPLATE.format(
        height=payload.get("height_cm") or "--",
        weight=payload.get("weight_kg") or "--",
        bmi=payload.get("bmi") if payload.get("bmi") is not None else "--",
        body_fat=payload.get("body_fat") if payload.get("body_fat") is not None else "--",
        sex=payload.get("sex") or "--",
        age=payload.get("age") or "--",
        bmr=payload.get("bmr") if payload.get("bmr") is not None else "--",
        tdee=payload.get("tdee") if payload.get("tdee") is not None else "--",
        target=payload.get("target") or "--",
        sport_level=payload.get("sport_level") or "--",
        diet_limit=payload.get("diet_limit") or "无特殊忌口",
        eat_scene=payload.get("eat_scene") or "自己做饭",
    )
    if payload.get("regenerate"):
        prompt += "\n\n请生成一套与此前完全不同的食谱，更换主要食材、搭配与烹饪方式。"
    user_message = (user_message or "").strip()
    if user_message:
        prompt += f"\n\n【用户本次补充要求】\n{user_message}"
    return prompt


def call_deepseek(prompt, history=None):
    """调用 DeepSeek Chat Completions API"""
    key = current_app.config.get("DEEPSEEK_API_KEY", "")
    base = current_app.config.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = current_app.config.get("DEEPSEEK_MODEL", "deepseek-chat")
    timeout = current_app.config.get("DEEPSEEK_TIMEOUT", 120)

    url = base + "/chat/completions"
    messages = [{"role": "system", "content": "你是专业的健身营养师，擅长为健身人群制定科学、可执行、口味友好的饮食方案。"}]
    for h in (history or [])[-8:]:
        role = h.get("role")
        content = (h.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content[:2000]})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 8000,
        "stream": False,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    # 推理模型默认思考耗时长、且容易把 token 全部花在思考上导致答案为空；
    # 默认关闭思考以快速返回最终答案，接口不支持该参数时自动回退。
    try:
        resp = requests.post(url, json={**payload, "thinking": {"type": "disabled"}}, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.HTTPError:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
    data = resp.json()
    message = data["choices"][0].get("message", {})
    content = message.get("content") or ""
    # 推理类模型可能把 token 全部花在思考过程上，最终答案为空；
    # 此时回退返回思考内容，保证「模型返回什么就显示什么」。
    if not content.strip():
        content = message.get("reasoning_content") or ""
    return content


def parse_plan_json(content):
    """从模型输出中稳健提取 JSON"""
    if not content:
        return None
    start = content.find("{")
    end = content.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(content[start:end + 1])
    except (json.JSONDecodeError, ValueError):
        return None


def mock_plan(data):
    """无 API Key 时的演示方案（标注 demo，便于前端联调）"""
    tdee = data.get("tdee") or 2200
    weight = data.get("weight_kg") or 70
    target_key = normalize_target(data.get("target"))[0]
    if target_key == "muscle":
        calories, protein_factor, note = tdee + 400, 1.8, "热量盈余 400kcal，配合力量训练增肌"
    elif target_key == "maintain":
        calories, protein_factor, note = tdee, 1.6, "维持当前体重，保持热量平衡"
    else:
        calories, protein_factor, note = tdee - 500, 2.0, "每日约 500kcal 热量缺口，温和减脂"
    protein = round(weight * protein_factor)
    fat = round(calories * 0.25 / 9)
    carbs = round((calories - protein * 4 - fat * 9) / 4)

    return {
        "summary": {
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "note": note,
        },
        "meals": [
            {
                "name": "早餐",
                "items": [
                    {"food": "全麦吐司", "weight": "2片(约70g)", "calories": 180},
                    {"food": "水煮蛋", "weight": "2个(约100g)", "calories": 140},
                    {"food": "脱脂牛奶", "weight": "250ml", "calories": 90},
                ],
                "note": "碳水打底，蛋白质充足",
            },
            {
                "name": "午餐",
                "items": [
                    {"food": "鸡胸肉", "weight": "150g", "calories": 240},
                    {"food": "糙米饭", "weight": "150g(熟重)", "calories": 175},
                    {"food": "西兰花", "weight": "200g", "calories": 70},
                ],
                "note": "少油快炒或水煮",
            },
            {
                "name": "晚餐",
                "items": [
                    {"food": "三文鱼", "weight": "120g", "calories": 260},
                    {"food": "紫薯", "weight": "150g", "calories": 130},
                    {"food": "菠菜沙拉", "weight": "150g", "calories": 60},
                ],
                "note": "睡前 3 小时完成进食",
            },
            {
                "name": "加餐（可选）",
                "items": [
                    {"food": "希腊酸奶", "weight": "150g", "calories": 120},
                    {"food": "巴旦木", "weight": "10粒(约15g)", "calories": 90},
                ],
                "note": "训练后补充更佳",
            },
        ],
        "water_tips": "每日饮水建议 2.0–2.5L，训练日额外增加 500ml；少量多次，避免一次性大量饮水。",
        "taboos": ["避免油炸、甜饮料与精加工零食", "晚餐后不再进食高热量夜宵"],
        "tips": [
            "蛋白质分配到每餐，保持血糖稳定与肌肉合成。",
            "当前体脂/体重情况建议优先保证训练质量，再调整热量。",
            "每周称重记录 2–3 次，结合围度判断进展。",
        ],
    }


def _fill_metrics(data):
    """补齐缺失的 BMI / BMR / TDEE 等指标"""
    result = compute_metrics(data)
    out = dict(data)
    if out.get("bmi") is None:
        out["bmi"] = result.get("bmi")
    if out.get("bmr") is None:
        out["bmr"] = result.get("bmr")
    if out.get("tdee") is None:
        out["tdee"] = result.get("tdee")
    if out.get("body_fat") is None:
        out["body_fat"] = result.get("body_fat")
    return out


@ai_bp.route("/diet-plan", methods=["POST"])
def generate_diet_plan():
    data = request.get_json(silent=True) or {}

    if not data.get("height_cm") or not data.get("weight_kg") or not data.get("age"):
        return jsonify(code=400, msg="请提供身高、体重与年龄"), 400

    target_key, target_label = normalize_target(data.get("target"))
    sport_level = ACTIVITY_LABELS.get(data.get("sport_level"), data.get("sport_level") or "轻度运动")
    gender = data.get("gender") or "male"
    sex = GENDER_LABELS.get(gender, "男")

    payload = _fill_metrics({
        "gender": gender,
        "age": data.get("age"),
        "activity_level": data.get("sport_level") or "light",
        "height_cm": data.get("height_cm"),
        "weight_kg": data.get("weight_kg"),
        "waist_cm": data.get("waist_cm"),
        "hip_cm": data.get("hip_cm"),
        "neck_cm": data.get("neck_cm"),
    })
    payload.update({
        "target": target_label,
        "sport_level": sport_level,
        "diet_limit": (data.get("diet_limit") or "").strip() or "无特殊忌口",
        "eat_scene": (data.get("eat_scene") or "").strip() or "自己做饭",
        "regenerate": bool(data.get("regenerate")),
        "sex": sex,
    })

    prompt = build_diet_prompt(payload, data.get("user_message"))
    model = current_app.config.get("DEEPSEEK_MODEL", "deepseek-chat")
    mock = current_app.config.get("DEEPSEEK_MOCK", False) or not current_app.config.get("DEEPSEEK_API_KEY", "")
    history = data.get("history") or []

    if mock:
        plan = mock_plan(payload)
        return jsonify(code=0, msg="success", data={
            "plan": plan,
            "raw_text": json.dumps(plan, ensure_ascii=False),
            "format": "json",
            "model": "demo",
            "mock": True,
        })

    try:
        content = call_deepseek(prompt, history)
    except requests.RequestException as e:
        return jsonify(code=502, msg=f"AI 服务调用失败：{e}"), 502
    except Exception as e:
        return jsonify(code=502, msg=f"AI 服务异常：{e}"), 502

    plan = parse_plan_json(content)
    if plan is None:
        return jsonify(code=0, msg="success", data={
            "plan": None, "raw_text": content, "format": "text", "model": model, "mock": False,
        })
    return jsonify(code=0, msg="success", data={
        "plan": plan, "raw_text": content, "format": "json", "model": model, "mock": False,
    })


def _current_user_id():
    from utils.auth import get_current_user
    user = get_current_user()
    return user.id if user else 0


@ai_bp.route("/diet-plans", methods=["GET"])
def list_diet_plans():
    user_id = _current_user_id()
    items = DietPlan.query.filter_by(user_id=user_id).order_by(DietPlan.id.desc()).limit(50).all()
    data = []
    for p in items:
        d = p.to_dict(exclude=["plan_json", "raw_text"])
        d["summary"] = None
        try:
            plan = json.loads(p.plan_json or "{}")
            d["summary"] = plan.get("summary")
        except (json.JSONDecodeError, AttributeError):
            pass
        data.append(d)
    return jsonify(code=0, msg="success", data={"items": data, "total": len(data)})


@ai_bp.route("/diet-plans", methods=["POST"])
def save_diet_plan():
    data = request.get_json(silent=True) or {}
    plan_json = data.get("plan_json")
    if not plan_json:
        return jsonify(code=400, msg="缺少方案内容 plan_json"), 400
    target_key, _ = normalize_target(data.get("target"))

    record = DietPlan(
        user_id=_current_user_id(),
        target=target_key,
        sport_level=(data.get("sport_level") or "")[:32],
        diet_limit=(data.get("diet_limit") or "")[:256],
        eat_scene=(data.get("eat_scene") or "")[:64],
        plan_json=plan_json if isinstance(plan_json, str) else json.dumps(plan_json, ensure_ascii=False),
        raw_text=data.get("raw_text") or "",
        model=(data.get("model") or "")[:64],
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(code=0, msg="方案已保存", data=record.to_dict(exclude=["plan_json", "raw_text"]))


@ai_bp.route("/diet-plans/<int:plan_id>", methods=["GET"])
def get_diet_plan(plan_id):
    user_id = _current_user_id()
    record = DietPlan.query.get(plan_id)
    if not record or record.user_id != user_id:
        return jsonify(code=404, msg="方案不存在"), 404
    d = record.to_dict()
    try:
        d["plan"] = json.loads(d.get("plan_json") or "{}")
    except (json.JSONDecodeError, TypeError):
        d["plan"] = None
    return jsonify(code=0, msg="success", data=d)


@ai_bp.route("/diet-plans/<int:plan_id>", methods=["DELETE"])
def delete_diet_plan(plan_id):
    user_id = _current_user_id()
    record = DietPlan.query.get(plan_id)
    if not record or record.user_id != user_id:
        return jsonify(code=404, msg="方案不存在"), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify(code=0, msg="已删除")


# ---------- 每日饮食打卡 ----------


def _num(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return date.today()


@ai_bp.route("/diet-logs", methods=["GET"])
def list_diet_logs():
    user_id = _current_user_id()
    days = request.args.get("days", 30, type=int)
    since = date.today() - timedelta(days=max(days, 1) - 1)
    items = DietLog.query.filter(
        DietLog.user_id == user_id,
        DietLog.log_date >= since
    ).order_by(DietLog.log_date.desc(), DietLog.id.desc()).all()
    return jsonify(code=0, msg="success", data={"items": [r.to_dict() for r in items], "total": len(items)})


@ai_bp.route("/diet-logs", methods=["POST"])
def save_diet_log():
    data = request.get_json(silent=True) or {}
    user_id = _current_user_id()
    calories = _num(data.get("calories"))
    if calories is None or calories <= 0:
        return jsonify(code=400, msg="请填写当日摄入热量"), 400

    log_date = _parse_date(data.get("log_date"))
    log = DietLog.query.filter_by(user_id=user_id, log_date=log_date).first()
    if not log:
        log = DietLog(user_id=user_id, log_date=log_date)
        db.session.add(log)

    log.calories = round(calories, 1)
    log.protein_g = _num(data.get("protein_g"))
    log.carbs_g = _num(data.get("carbs_g"))
    log.fat_g = _num(data.get("fat_g"))
    log.note = (data.get("note") or "")[:256]
    db.session.commit()
    return jsonify(code=0, msg="打卡成功", data=log.to_dict())


@ai_bp.route("/diet-logs/<int:log_id>", methods=["DELETE"])
def delete_diet_log(log_id):
    user_id = _current_user_id()
    log = DietLog.query.get(log_id)
    if not log or log.user_id != user_id:
        return jsonify(code=404, msg="打卡记录不存在"), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify(code=0, msg="已删除")


# ---------- 周期复盘（近 7 天身材 + 饮食汇总） ----------


def _week_summary(user_id):
    since = date.today() - timedelta(days=6)
    records = BodyRecord.query.filter(
        BodyRecord.user_id == user_id,
        BodyRecord.record_date >= since
    ).order_by(BodyRecord.record_date.asc(), BodyRecord.id.asc()).all()
    logs = DietLog.query.filter(
        DietLog.user_id == user_id,
        DietLog.log_date >= since
    ).order_by(DietLog.log_date.asc()).all()

    def diff(field):
        vals = [getattr(r, field) for r in records if getattr(r, field) is not None]
        if len(vals) < 2:
            return None
        return {"start": vals[0], "end": vals[-1], "change": round(vals[-1] - vals[0], 2)}

    tdee = None
    for r in reversed(records):
        if r.tdee:
            tdee = r.tdee
            break
    avg_cal = round(sum(l.calories for l in logs) / len(logs), 1) if logs else None

    return {
        "record_count": len(records),
        "weight": diff("weight_kg"),
        "bmi": diff("bmi"),
        "body_fat": diff("body_fat"),
        "diet": {
            "log_days": len(logs),
            "avg_calories": avg_cal,
            "tdee": tdee,
            "avg_diff": round(avg_cal - tdee, 1) if avg_cal is not None and tdee else None,
        },
    }


def build_review_prompt(s):
    lines = []
    lines.append("你是专业健身教练与营养师，请根据过去 7 天的身材数据与饮食打卡情况，输出一份简洁的一周健身饮食复盘：")
    lines.append("【身材数据变化】")
    if s["weight"]:
        lines.append(f"体重：{s['weight']['start']}kg → {s['weight']['end']}kg（变化 {s['weight']['change']:+}kg）")
    else:
        lines.append("体重：本周记录不足 2 次，暂无法计算变化")
    if s["bmi"]:
        lines.append(f"BMI：{s['bmi']['start']} → {s['bmi']['end']}")
    if s["body_fat"]:
        lines.append(f"体脂率：{s['body_fat']['start']}% → {s['body_fat']['end']}%")
    lines.append("【饮食执行】")
    d = s["diet"]
    lines.append(f"打卡天数：{d['log_days']}/7")
    if d["avg_calories"] is not None:
        lines.append(f"日均摄入：{d['avg_calories']} kcal")
    if d["tdee"]:
        lines.append(f"每日消耗 TDEE：{d['tdee']} kcal")
    if d["avg_diff"] is not None:
        lines.append(f"日均热量差值：{d['avg_diff']:+} kcal（相对 TDEE）")
    lines.append("【输出要求】")
    lines.append("1. 用 3-5 句话总结本周整体表现；")
    lines.append("2. 指出做得好的 1-2 点；")
    lines.append("3. 指出需要改进的 1-2 点；")
    lines.append("4. 给出下周 2-3 条可执行建议。")
    lines.append("不要复杂 markdown，分段清晰，适配网页展示。")
    return "\n".join(lines)


def mock_review(s):
    parts = ["【本周复盘】"]
    w = s["weight"]
    if w:
        direction = "下降" if w["change"] < 0 else "上升" if w["change"] > 0 else "保持"
        parts.append(f"本周体重{direction} {abs(w['change']):.1f}kg（{w['start']} → {w['end']}kg），与当前阶段目标基本一致。")
    else:
        parts.append("本周身材记录较少，建议增加记录频率，才能更准确判断趋势。")
    d = s["diet"]
    if d["log_days"]:
        diff_txt = ""
        if d["avg_diff"] is not None:
            if d["avg_diff"] > 0:
                diff_txt = f"，日均超出消耗 {d['avg_diff']:.0f}kcal，与减脂目标冲突"
            else:
                diff_txt = f"，日均低于消耗 {-d['avg_diff']:.0f}kcal，符合减脂方向"
        parts.append(f"本周饮食打卡 {d['log_days']} 天，日均摄入 {d['avg_calories']:.0f}kcal{diff_txt}。")
        parts.append("做得好的：坚持打卡本身就是最大的进步，能持续获得数据反馈。")
        parts.append("待改进：打卡天数建议做到 7/7，并尽量同时记录三大营养素。")
    else:
        parts.append("本周暂无饮食打卡，下周建议从每天记录摄入热量开始。")
    parts.append("下周建议：1）保持规律训练与充足睡眠；2）饮食以高蛋白、高纤维为主；3）每周固定 2-3 次称重与围度测量。")
    return "\n".join(parts)


@ai_bp.route("/weekly-review", methods=["POST"])
def weekly_review():
    user_id = _current_user_id()
    summary = _week_summary(user_id)
    prompt = build_review_prompt(summary)
    mock = current_app.config.get("DEEPSEEK_MOCK", False) or not current_app.config.get("DEEPSEEK_API_KEY", "")

    if mock:
        return jsonify(code=0, msg="success", data={
            "review_text": mock_review(summary),
            "summary": summary,
            "mock": True,
        })
    try:
        content = call_deepseek(prompt)
    except requests.RequestException as e:
        return jsonify(code=502, msg=f"AI 服务调用失败：{e}"), 502
    except Exception as e:
        return jsonify(code=502, msg=f"AI 服务异常：{e}"), 502
    return jsonify(code=0, msg="success", data={
        "review_text": content,
        "summary": summary,
        "mock": False,
    })
