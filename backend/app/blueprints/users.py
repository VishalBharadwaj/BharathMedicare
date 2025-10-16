from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import UserRole
from app.utils.auth import require_auth, require_role, get_current_user
from app.utils.audit import AuditLogger
import uuid

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user's profile"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404

        # Remove sensitive information
        profile_data = {
            'id': str(current_user['_id']),
            'email': current_user['email'],
            'first_name': current_user['first_name'],
            'last_name': current_user['last_name'],
            'role': current_user['role'],
            'is_active': current_user['is_active'],
            'mfa_enabled': current_user.get('mfa_enabled', False),
            'last_login': current_user.get('last_login'),
            'created_at': current_user['created_at'].isoformat(),
            'profile': current_user.get('profile', {})
        }

        # Add role-specific data
        if current_user['role'] == UserRole.PATIENT.value:
            profile_data.update({
                'date_of_birth': current_user.get('date_of_birth'),
                'medical_record_number': current_user.get('medical_record_number'),
                'emergency_contact': current_user.get('emergency_contact', {}),
                'insurance_info': current_user.get('insurance_info', {})
            })
        elif current_user['role'] == UserRole.DOCTOR.value:
            profile_data.update({
                'license_number': current_user.get('license_number'),
                'specialization': current_user.get('specialization'),
                'department': current_user.get('department'),
                'hospital_id': current_user.get('hospital_id')
            })
        elif current_user['role'] == UserRole.ADMIN.value:
            profile_data.update({
                'admin_level': current_user.get('admin_level'),
                'permissions': current_user.get('permissions', [])
            })

        return jsonify({
            'profile': profile_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'PROFILE_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@users_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update current user's profile"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404

        data = request.get_json()
        
        # Define allowed fields for update
        allowed_fields = ['first_name', 'last_name', 'profile']
        
        # Add role-specific allowed fields
        if current_user['role'] == UserRole.PATIENT.value:
            allowed_fields.extend(['emergency_contact', 'insurance_info'])
        elif current_user['role'] == UserRole.DOCTOR.value:
            allowed_fields.extend(['specialization', 'department'])

        # Filter update data to only allowed fields
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({
                'error': {
                    'code': 'NO_UPDATE_DATA',
                    'message': 'No valid fields provided for update',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 400

        # Update user profile
        success = db_manager.update_one(
            'users',
            {'_id': current_user['_id']},
            update_data
        )

        if success:
            # Log profile update
            AuditLogger.log_action(
                user_id=str(current_user['_id']),
                action='PROFILE_UPDATED',
                resource_type='USER',
                resource_id=str(current_user['_id']),
                details={'updated_fields': list(update_data.keys())}
            )

            return jsonify({
                'message': 'Profile updated successfully',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': {
                    'code': 'UPDATE_FAILED',
                    'message': 'Failed to update profile',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 500

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'UPDATE_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@users_bp.route('/search', methods=['GET'])
@require_role(UserRole.DOCTOR, UserRole.ADMIN)
def search_users(current_user):
    """Search for users (doctors and admins only)"""
    try:
        query = request.args.get('q', '').strip()
        role_filter = request.args.get('role')
        
        if not query:
            return jsonify({
                'error': {
                    'code': 'MISSING_QUERY',
                    'message': 'Search query is required',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 400

        # Build search filter
        search_filter = {
            '$or': [
                {'first_name': {'$regex': query, '$options': 'i'}},
                {'last_name': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}}
            ],
            'is_active': True
        }

        # Add role filter if specified
        if role_filter:
            search_filter['role'] = role_filter

        # Doctors can only search for patients and other doctors
        if current_user['role'] == UserRole.DOCTOR.value:
            search_filter['role'] = {'$in': [UserRole.PATIENT.value, UserRole.DOCTOR.value]}

        # Find users
        users = db_manager.find_many('users', search_filter, limit=20)

        # Format results (remove sensitive information)
        results = []
        for user in users:
            user_data = {
                'id': str(user['_id']),
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': user['email'],
                'role': user['role']
            }
            
            # Add role-specific information
            if user['role'] == UserRole.DOCTOR.value:
                user_data.update({
                    'specialization': user.get('specialization'),
                    'department': user.get('department')
                })
            elif user['role'] == UserRole.PATIENT.value:
                user_data.update({
                    'medical_record_number': user.get('medical_record_number')
                })
            
            results.append(user_data)

        # Log search action
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='USER_SEARCH',
            resource_type='USER',
            resource_id='multiple',
            details={'query': query, 'role_filter': role_filter, 'results_count': len(results)}
        )

        return jsonify({
            'users': results,
            'count': len(results),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'SEARCH_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500