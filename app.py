import os
import datetime
from flask import Flask, render_template
from config import Config
from models import db, login_manager
from models.user import User
from utils.helpers import create_default_users

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)

    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)

    db_path = os.path.join(db_dir, 'bluelens.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.utcnow}

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
        create_default_users()

    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print(" BlueLens - Security Log & IOC Analyzer")
    print("=" * 50)
    print(" Running on http://127.0.0.1:5000")
    print(" Admin  : admin / admin123")
    print(" Analyst: analyst / analyst123")
    print("=" * 50)
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except ImportError:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
