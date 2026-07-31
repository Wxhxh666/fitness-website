from flask import jsonify, request
from . import exercises_bp
from models.exercise import Exercise, ExerciseCategory
from models import db


@exercises_bp.route("/categories", methods=["GET"])
def get_categories():
    qs = ExerciseCategory.query.filter_by(is_active=True).order_by(ExerciseCategory.sort_order).all()
    return jsonify(code=0, msg="success", data=[c.to_dict() for c in qs])


@exercises_bp.route("", methods=["GET"])
def get_exercises():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    keyword = request.args.get("keyword")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 50, type=int)

    q = Exercise.query.filter_by(is_active=True)
    if category:
        q = q.filter_by(category=category)
    if difficulty:
        q = q.filter_by(difficulty=difficulty)
    if keyword:
        q = q.filter(Exercise.name.contains(keyword))

    total = q.count()
    items = q.order_by(Exercise.sort_order, Exercise.id).offset((page - 1) * page_size).limit(page_size).all()

    return jsonify(code=0, msg="success", data={
        "items": [ex.to_dict() for ex in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@exercises_bp.route("/<int:exercise_id>", methods=["GET"])
def get_exercise_detail(exercise_id):
    ex = Exercise.query.get_or_404(exercise_id)
    return jsonify(code=0, msg="success", data=ex.to_dict())
