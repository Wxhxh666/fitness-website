from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

    # CORS
    origins = app.config.get("CORS_ORIGINS", "*")
    CORS(app, resources={r"/api/*": {"origins": origins.split(","), "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}})

    # DB
    db.init_app(app)

    # Register blueprints
    from routes.exercises import exercises_bp
    from routes.plans import plans_bp
    from routes.body_metrics import body_metrics_bp
    from routes.contact import contact_bp
    from routes.site import site_bp
    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.admin import admin_bp
    from routes.user_plans import user_plans_bp

    app.register_blueprint(exercises_bp, url_prefix="/api/exercises")
    app.register_blueprint(plans_bp, url_prefix="/api/plans")
    app.register_blueprint(body_metrics_bp, url_prefix="/api/body-metrics")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(site_bp, url_prefix="/api/site")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(user_plans_bp, url_prefix="/api/plans/user")

    # Root - API index
    @app.route("/api", methods=["GET"])
    def api_index():
        return jsonify(code=0, msg="FITLUXE API v1.0", data={
            "docs": "/api/docs",
            "health": "/api/health",
            "endpoints": [
                "GET  /api/exercises/categories",
                "GET  /api/exercises[?category=&difficulty=&keyword=]",
                "GET  /api/exercises/:id",
                "GET  /api/plans/goals",
                "GET  /api/plans[?goal=&difficulty=]",
                "GET  /api/plans/:id",
                "GET  /api/body-metrics[?user_id=]",
                "POST /api/body-metrics/bmi",
                "GET  /api/body-metrics/measurements[?user_id=]",
                "PUT  /api/body-metrics/measurements/:id",
                "GET  /api/body-metrics/history[?metric_key=&days=]",
                "POST /api/contact",
                "GET  /api/site/contact-info",
            ],
        })

    # Health check
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify(code=0, msg="healthy")

    # Root redirect
    @app.route("/", methods=["GET"])
    def root():
        return jsonify(
            code=0,
            msg="FITLUXE API",
            data={
                "api": "/api",
                "docs": "See api.md in the project root for full documentation.",
            },
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)



