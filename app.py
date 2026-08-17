import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.seller import seller_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(admin_bp)

    # Global Context Processors
    @app.context_processor
    def inject_globals():
        return {
            'site_name': 'GlobalExportHub',
            'current_year': 2026
        }

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[Database Warning] Could not connect to primary DB: {e}")
            if app.config.get('USE_SQLITE_FALLBACK'):
                print("[Database Info] Falling back to SQLite database...")
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exportweb.db'
                db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
