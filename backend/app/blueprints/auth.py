from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import UserSchema, PatientSchema, DoctorSchema, AdminSchema, UserRole
from app.utils.auth import AuthManager, require_auth
from app.utils.audit import AuditLogger
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': f'Missing required field: {field}',
                        'timestamp': datetime.utcnow().isoformat(),
                        'requestId': str(uuid.uuid4())
                    }
                }), 400
        
        # Check if user already exists
        existing_user = db_manager.find_one('users', {'email': data['email']})
        if existing_user:
            return jsonify({
                'error': {
                    'code': 'USER_EXISTS',
                    'message': 'User with this email already exists',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 409
        
        # Hash password
        password_hash = AuthManager.hash_password(data['password'])
        
        # Create user based on role
        role = UserRole(data['role'])
        if role == UserRole.PATIENT:
            user_schema = PatientSchema(
                email=data['email'],
                password_hash=password_hash,
                first_name=data['first_name'],
                last_name=data['last_name'],
                date_of_birth=data.get('date_of_birth'),
                medical_record_number=data.get('medical_record_number', str(uuid.uuid4())),
                emergency_contact=data.get('emergency_contact', {}),
                insurance_info=data.get('insurance_info', {})
            )
        elif role == UserRole.DOCTOR:
            user_schema = DoctorSchema(
                email=data['email'],
                password_hash=password_hash,
                first_name=data['first_name'],
                last_name=data['last_name'],
                license_number=data.get('license_number'),
                specialization=data.get('specialization'),
                department=data.get('department'),
                hospital_id=data.get('hospital_id')
            )
        elif role == UserRole.ADMIN:
            user_schema = AdminSchema(
                email=data['email'],
                password_hash=password_hash,
                first_name=data['first_name'],
                last_name=data['last_name'],
                admin_level=data.get('admin_level', 1),
                permissions=data.get('permissions', [])
            )
        
        # Insert user into database
        user_id = db_manager.insert_one('users', user_schema.__dict__)
        
        # Log registration
        AuditLogger.log_action(
            user_id=user_id,
            action='USER_REGISTERED',
            resource_type='USER',
            resource_id=user_id
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'REGISTRATION_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT tokens"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        mfa_token = data.get('mfa_token')
        
        if not email or not password:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Email and password are required',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 400
        
        # Find user
        user = db_manager.find_one('users', {'email': email})
        if not user or not user.get('is_active'):
            AuditLogger.log_login_attempt('unknown', False, 'User not found or inactive')
            return jsonify({
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 401
        
        # Verify password
        if not AuthManager.verify_password(password, user['password_hash']):
            AuditLogger.log_login_attempt(str(user['_id']), False, 'Invalid password')
            return jsonify({
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 401
        
        # Check MFA if enabled
        if user.get('mfa_enabled'):
            if not mfa_token:
                return jsonify({
                    'error': {
                        'code': 'MFA_REQUIRED',
                        'message': 'MFA token is required',
                        'timestamp': datetime.utcnow().isoformat(),
                        'requestId': str(uuid.uuid4())
                    }
                }), 401
            
            if not AuthManager.verify_mfa_token(user['mfa_secret'], mfa_token):
                AuditLogger.log_login_attempt(str(user['_id']), False, 'Invalid MFA token')
                return jsonify({
                    'error': {
                        'code': 'INVALID_MFA',
                        'message': 'Invalid MFA token',
                        'timestamp': datetime.utcnow().isoformat(),
                        'requestId': str(uuid.uuid4())
                    }
                }), 401
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user['_id']))
        refresh_token = create_refresh_token(identity=str(user['_id']))
        
        # Update last login
        db_manager.update_one('users', {'_id': user['_id']}, {'last_login': datetime.utcnow()})
        
        # Log successful login
        AuditLogger.log_login_attempt(str(user['_id']), True)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'role': user['role'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LOGIN_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'REFRESH_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@auth_bp.route('/validate', methods=['GET'])
@require_auth
def validate_token():
    """Validate JWT token"""
    try:
        current_user_id = get_jwt_identity()
        user = db_manager.find_one('users', {'_id': ObjectId(current_user_id)})
        
        if not user or not user.get('is_active'):
            return jsonify({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Token is invalid or user is inactive',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'role': user['role'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500