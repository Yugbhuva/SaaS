from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Import models
    from app.models.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import bp as auth_bp
    from app.billing import bp as billing_bp
    from app.license import bp as license_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(license_bp, url_prefix='/license')
    
    # Main routes
    from flask import render_template, redirect, url_for
    from flask_login import login_required, current_user
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', user=current_user)
    
    @app.route('/pricing')
    def pricing():
        return render_template('pricing.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app