from flask import jsonify, request
from . import plans_bp
from models.plan import Plan, PlanGoal


@plans_bp.route("/goals", methods=["GET"])
def get_goals():
    qs = PlanGoal.query.order_by(PlanGoal.sort_order).all()
    return jsonify(code=0, msg="success", data=[g.to_dict() for g in qs])


@plans_bp.route("", methods=["GET"])
def get_plans():
    goal = request.args.get("goal")
    difficulty = request.args.get("difficulty")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)

    q = Plan.query.filter_by(is_active=True)
    if goal:
        q = q.filter_by(goal=goal)
    if difficulty:
        q = q.filter_by(difficulty=difficulty)

    total = q.count()
    items = q.order_by(Plan.sort_order, Plan.id).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify(code=0, msg="success", data={
        "items": [p.to_dict() for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@plans_bp.route("/<int:plan_id>", methods=["GET"])
def get_plan_detail(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    return jsonify(code=0, msg="success", data=plan.to_dict())
