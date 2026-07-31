from flask import jsonify, request
from . import body_metrics_bp
from utils.auth import get_current_user, require_auth
from models.body_metric import BodyMetric
from models import db
from datetime import datetime, timedelta


@body_metrics_bp.route("", methods=["GET"])
def get_metrics():
    user = get_current_user()
    user_id = user.id if user else 0
    keys = ["weight", "body_fat", "muscle_mass", "bmr"]
    qs = BodyMetric.query.filter(
        BodyMetric.user_id == user_id,
        BodyMetric.key.in_(keys)
    ).order_by(BodyMetric.id).all()
    return jsonify(code=0, msg="success", data=[m.to_dict() for m in qs])


@body_metrics_bp.route("/bmi", methods=["POST"])
def calculate_bmi():
    data = request.get_json(silent=True) or {}
    height_cm = data.get("height_cm")
    weight_kg = data.get("weight_kg")
    if not height_cm or not weight_kg:
        return jsonify(code=400, msg="请提供 height_cm 和 weight_kg"), 400

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "underweight"
        label = "偏瘦"
    elif bmi < 25:
        category = "normal"
        label = "正常范围"
    elif bmi < 30:
        category = "overweight"
        label = "超重"
    else:
        category = "obese"
        label = "肥胖"

    return jsonify(code=0, msg="success", data={
        "bmi": bmi,
        "category": category,
        "category_label": label,
        "healthy_range": "18.5 – 24.9"
    })


@body_metrics_bp.route("/measurements", methods=["GET"])
def get_measurements():
    user = get_current_user()
    user_id = user.id if user else 0
    keys = ["chest", "waist", "hips", "arm", "thigh", "calf"]
    qs = BodyMetric.query.filter(
        BodyMetric.user_id == user_id,
        BodyMetric.key.in_(keys)
    ).order_by(BodyMetric.id).all()
    return jsonify(code=0, msg="success", data=[m.to_dict() for m in qs])


@body_metrics_bp.route("/measurements/<int:measurement_id>", methods=["PUT"])
@require_auth
def update_measurement(measurement_id):
    m = BodyMetric.query.get_or_404(measurement_id)
    data = request.get_json(silent=True) or {}
    new_value = data.get("value")
    if new_value is None:
        return jsonify(code=400, msg="请提供 value"), 400

    previous = m.value
    m.value = float(new_value)
    m.change = round(m.value - previous, 1)
    m.trend = "up" if m.change > 0 else "down" if m.change < 0 else "flat"
    m.recorded_at = datetime.utcnow()
    db.session.commit()

    result = m.to_dict()
    result["previous_value"] = previous
    return jsonify(code=0, msg="success", data=result)


@body_metrics_bp.route("/history", methods=["GET"])
def get_history():
    metric_key = request.args.get("metric_key")
    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    q = BodyMetric.query.filter(BodyMetric.recorded_at >= since)
    if metric_key:
        q = q.filter_by(key=metric_key)

    rows = q.order_by(BodyMetric.key, BodyMetric.recorded_at).all()

    grouped = {}
    for r in rows:
        grouped.setdefault(r.key, []).append({
            "date": r.recorded_at.strftime("%Y-%m-%d") if isinstance(r.recorded_at, datetime) else str(r.recorded_at)[:10],
            "value": r.value,
        })

    data = [{"metric_key": k, "records": v} for k, v in grouped.items()]
    return jsonify(code=0, msg="success", data=data)



