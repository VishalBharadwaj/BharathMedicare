import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import UserRole
import pyotp
import qrcode
import io
import base64

class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=current_app.config['BCRYPT_LOG_ROUNDS'])
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def generate_mfa_secret() -> str:
        """Generate MFA secret for TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(email: str, secret: str) -> str:
        """Generate QR code for MFA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="Medical Records System"
        )
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_mfa_token(secret: str, token: str) -> bool:
        """Verify MFA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

def require_auth(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Invalid or expired token',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': request.headers.get('X-Request-ID', 'unknown')
                }
            }), 401
    return decorated_function

def require_role(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # Get user from database
                user = db_manager.find_one('users', {'_id': ObjectId(current_user_id)})
                if not user or not user.get('is_active'):
                    return jsonify({
                        'error': {
                            'code': 'UNAUTHORIZED',
                            'message': 'User not found or inactive',
                            'timestamp': datetime.utcnow().isoformat(),
                            'requestId': request.headers.get('X-Request-ID', 'unknown')
                        }
                    }), 401
                
                # Check role
                user_role = user.get('role')
                if user_role not in [role.value for role in allowed_roles]:
                    return jsonify({
                        'error': {
                            'code': 'FORBIDDEN',
                            'message': f'Access denied. Required roles: {[role.value for role in allowed_roles]}',
                            'timestamp': datetime.utcnow().isoformat(),
                            'requestId': request.headers.get('X-Request-ID', 'unknown')
                        }
                    }), 403
                
                # Add user to kwargs for use in the route
                kwargs['current_user'] = user
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': {
                        'code': 'AUTHORIZATION_ERROR',
                        'message': str(e),
                        'timestamp': datetime.utcnow().isoformat(),
                        'requestId': request.headers.get('X-Request-ID', 'unknown')
                    }
                }), 500
        return decorated_function
    return decorator

def get_current_user():
    """Get current authenticated user"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return db_manager.find_one('users', {'_id': ObjectId(current_user_id)})
    except:
        return None