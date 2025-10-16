from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import UserRole
from app.utils.auth import require_role
from app.utils.audit import AuditLogger
import uuid

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/statistics', methods=['GET'])
@require_role(UserRole.ADMIN)
def get_statistics(current_user):
    """Get system statistics for admin dashboard"""
    try:
        # Count doctors
        doctors_count = db_manager.count_documents('users', {
            'role': UserRole.DOCTOR.value,
            'is_active': True
        })
        
        # Count patients
        patients_count = db_manager.count_documents('users', {
            'role': UserRole.PATIENT.value,
            'is_active': True
        })
        
        # Count medical records
        records_count = db_manager.count_documents('medical_documents', {
            'is_deleted': False
        })
        
        # Count active access grants
        access_grants_count = db_manager.count_documents('access_grants', {
            'is_active': True,
            '$or': [
                {'expires_at': {'$gt': datetime.utcnow()}},
                {'expires_at': None}
            ]
        })
        
        # Count total users
        total_users = db_manager.count_documents('users', {
            'is_active': True
        })
        
        # Count admins
        admins_count = db_manager.count_documents('users', {
            'role': UserRole.ADMIN.value,
            'is_active': True
        })
        
        # Log statistics access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='STATISTICS_VIEWED',
            resource_type='SYSTEM',
            resource_id='statistics'
        )
        
        return jsonify({
            'statistics': {
                'doctors': doctors_count,
                'patients': patients_count,
                'records': records_count,
                'access_grants': access_grants_count,
                'total_users': total_users,
                'admins': admins_count
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'STATISTICS_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@admin_bp.route('/users', methods=['GET'])
@require_role(UserRole.ADMIN)
def list_all_users(current_user):
    """List all users in the system"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        
        # Get role filter
        role_filter = request.args.get('role')
        
        # Build query
        query = {'is_active': True}
        if role_filter:
            query['role'] = role_filter
        
        # Find users
        users = db_manager.find_many(
            'users',
            query,
            limit=limit,
            skip=skip,
            sort=[('created_at', -1)]
        )
        
        # Count total users
        total_count = db_manager.count_documents('users', query)
        
        # Format response
        user_list = []
        for user in users:
            user_data = {
                'id': str(user['_id']),
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role'],
                'is_active': user['is_active'],
                'created_at': user['created_at'].isoformat(),
                'last_login': user.get('last_login').isoformat() if user.get('last_login') else None
            }
            
            # Add role-specific data
            if user['role'] == UserRole.DOCTOR.value:
                user_data.update({
                    'license_number': user.get('license_number'),
                    'specialization': user.get('specialization'),
                    'department': user.get('department')
                })
            elif user['role'] == UserRole.PATIENT.value:
                user_data.update({
                    'date_of_birth': user.get('date_of_birth'),
                    'medical_record_number': user.get('medical_record_number')
                })
            
            user_list.append(user_data)
        
        # Log access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='USERS_LISTED',
            resource_type='USER',
            resource_id='multiple',
            details={'count': len(user_list), 'role_filter': role_filter}
        )
        
        return jsonify({
            'users': user_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LIST_USERS_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@admin_bp.route('/users/<user_id>', methods=['GET'])
@require_role(UserRole.ADMIN)
def get_user_details(user_id, current_user):
    """Get detailed information about a specific user"""
    try:
        # Find user
        user = db_manager.find_one('users', {
            '_id': ObjectId(user_id)
        })
        
        if not user:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404
        
        # Format user data
        user_data = {
            'id': str(user['_id']),
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role'],
            'is_active': user['is_active'],
            'mfa_enabled': user.get('mfa_enabled', False),
            'created_at': user['created_at'].isoformat(),
            'last_login': user.get('last_login').isoformat() if user.get('last_login') else None
        }
        
        # Add role-specific data
        if user['role'] == UserRole.DOCTOR.value:
            user_data.update({
                'license_number': user.get('license_number'),
                'specialization': user.get('specialization'),
                'department': user.get('department'),
                'hospital_id': user.get('hospital_id')
            })
        elif user['role'] == UserRole.PATIENT.value:
            user_data.update({
                'date_of_birth': user.get('date_of_birth'),
                'medical_record_number': user.get('medical_record_number'),
                'emergency_contact': user.get('emergency_contact', {}),
                'insurance_info': user.get('insurance_info', {})
            })
        elif user['role'] == UserRole.ADMIN.value:
            user_data.update({
                'admin_level': user.get('admin_level'),
                'permissions': user.get('permissions', [])
            })
        
        # Log access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='USER_VIEWED',
            resource_type='USER',
            resource_id=user_id
        )
        
        return jsonify({
            'user': user_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_USER_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@admin_bp.route('/users/<user_id>/toggle-status', methods=['POST'])
@require_role(UserRole.ADMIN)
def toggle_user_status(user_id, current_user):
    """Activate or deactivate a user account"""
    try:
        # Find user
        user = db_manager.find_one('users', {'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404
        
        # Prevent admin from deactivating themselves
        if str(user['_id']) == str(current_user['_id']):
            return jsonify({
                'error': {
                    'code': 'CANNOT_DEACTIVATE_SELF',
                    'message': 'Cannot deactivate your own account',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 400
        
        # Toggle status
        new_status = not user.get('is_active', True)
        
        success = db_manager.update_one(
            'users',
            {'_id': ObjectId(user_id)},
            {'is_active': new_status}
        )
        
        if success:
            # Log action
            AuditLogger.log_action(
                user_id=str(current_user['_id']),
                action='USER_STATUS_CHANGED',
                resource_type='USER',
                resource_id=user_id,
                details={'new_status': 'active' if new_status else 'inactive'}
            )
            
            return jsonify({
                'message': f'User {"activated" if new_status else "deactivated"} successfully',
                'is_active': new_status,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': {
                    'code': 'UPDATE_FAILED',
                    'message': 'Failed to update user status',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 500
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'TOGGLE_STATUS_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500
