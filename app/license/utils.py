import jwt
import secrets
import string
from datetime import datetime, timedelta
from config import Config

def generate_jwt_license(user_email, product_name, expires_days=365):
    """Generate a JWT-based license token"""
    payload = {
        'user_email': user_email,
        'product_name': product_name,
        'issued_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(days=expires_days)).isoformat()
    }
    
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token

def validate_jwt_license(token):
    """Validate a JWT license token"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        
        # Check expiration
        expires_at = datetime.fromisoformat(payload['expires_at'])
        if datetime.utcnow() > expires_at:
            return None, 'License expired'
        
        return payload, None
    
    except jwt.ExpiredSignatureError:
        return None, 'License expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid license token'

def generate_simple_key(length=20):
    """Generate a simple alphanumeric license key"""
    chars = string.ascii_uppercase + string.digits
    key = ''.join(secrets.choice(chars) for _ in range(length))
    return '-'.join([key[i:i+5] for i in range(0, length, 5)])