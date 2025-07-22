from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import string

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Subscription fields
    stripe_customer_id = db.Column(db.String(100))
    subscription_status = db.Column(db.String(50), default='inactive')
    subscription_id = db.Column(db.String(100))
    current_period_end = db.Column(db.DateTime)
    
    # Relationships
    licenses = db.relationship('License', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_active_subscription(self):
        return self.subscription_status in ['active', 'trialing']
    
    def subscription_expires_soon(self):
        if self.current_period_end:
            return self.current_period_end <= datetime.utcnow() + timedelta(days=7)
        return False

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    max_activations = db.Column(db.Integer, default=1)
    current_activations = db.Column(db.Integer, default=0)
    
    def generate_key(self):
        """Generate a secure license key"""
        chars = string.ascii_uppercase + string.digits
        key = ''.join(secrets.choice(chars) for _ in range(20))
        # Format as XXXXX-XXXXX-XXXXX-XXXXX
        formatted_key = '-'.join([key[i:i+5] for i in range(0, 20, 5)])
        self.key = formatted_key
        return formatted_key
    
    def is_valid(self):
        """Check if license is valid"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at <= datetime.utcnow():
            return False
        if self.current_activations >= self.max_activations:
            return False
        return True