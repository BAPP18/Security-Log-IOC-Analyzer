import datetime
import os

from flask import Flask, jsonify, render_template
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import db, login_manager
from models.user import User
from utils.helpers import create_default_users

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    for folder_key in ("UPLOAD_FOLDER", "EXPORT_FOLDER", "REPORT_FOLDER", "LOG_FOLDER"):
        os.makedirs(app.config[folder_key], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            service="bluelens",
            environment=app.config.get("APP_ENV", "unknown"),
        )

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return render_template("500.html"), 500

    @app.context_processor
    def inject_now():
        return {"now": datetime.datetime.utcnow}

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.upload import upload_bp
    from routes.ioc_routes import ioc_bp
    from routes.export import export_bp
    from routes.report import report_bp
    from routes.activity_log import activity_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(ioc_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(activity_bp)

    with app.app_context():
        db.create_all()
        if app.config.get("SEED_DEMO_USERS"):
            create_default_users()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=app.config.get("APP_ENV") != "production",
        host="127.0.0.1",
        port=5000,
        use_reloader=False,
    )
