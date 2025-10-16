from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import AccessGrantSchema, AccessLevel, UserRole
from app.utils.auth import require_auth, require_role, get_current_user
from app.utils.audit import AuditLogger
import uuid

access_bp = Blueprint('access', __name__)

@access_bp.route('/grant', methods=['POST'])
@require_auth
def grant_access():
    """Grant access to a medical document"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 401

        data = request.get_json()
        
        # Validate required fields
        required_fields = ['document_id', 'grantee_id', 'access_level']
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

        # Validate access level
        try:
            access_level = AccessLevel(data['access_level'])
        except ValueError:
            return jsonify({
                'error': {
                    'code': 'INVALID_ACCESS_LEVEL',
                    'message': f'Invalid access level: {data["access_level"]}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 400

        # Find the document
        document = db_manager.find_one('medical_documents', {
            '_id': ObjectId(data['document_id']),
            'is_deleted': False
        })
        
        if not document:
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_FOUND',
                    'message': 'Medical document not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404

        # Check if current user can grant access
        can_grant = False
        
        # Patient can grant access to their own records
        if (current_user['role'] == UserRole.PATIENT.value and 
            str(current_user['_id']) == document['patient_id']):
            can_grant = True
        
        # Doctor can grant access to records they created
        elif (current_user['role'] == UserRole.DOCTOR.value and 
              str(current_user['_id']) == document['doctor_id']):
            can_grant = True
        
        # Admin can grant access to any record
        elif current_user['role'] == UserRole.ADMIN.value:
            can_grant = True

        if not can_grant:
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'You do not have permission to grant access to this document',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 403

        # Verify grantee exists
        grantee = db_manager.find_one('users', {
            '_id': ObjectId(data['grantee_id']),
            'is_active': True
        })
        
        if not grantee:
            return jsonify({
                'error': {
                    'code': 'GRANTEE_NOT_FOUND',
                    'message': 'Grantee user not found or inactive',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404

        # Check if access grant already exists
        existing_grant = db_manager.find_one('access_grants', {
            'grantee_id': data['grantee_id'],
            'document_id': data['document_id'],
            'is_active': True
        })

        if existing_grant:
            # Update existing grant
            update_data = {
                'access_level': access_level.value,
                'granted_by': str(current_user['_id']),
                'reason': data.get('reason', ''),
                'expires_at': datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
            }
            
            success = db_manager.update_one(
                'access_grants',
                {'_id': existing_grant['_id']},
                update_data
            )
            
            grant_id = str(existing_grant['_id'])
            action = 'ACCESS_GRANT_UPDATED'
        else:
            # Create new access grant
            access_grant = AccessGrantSchema(
                grantor_id=str(current_user['_id']),
                grantee_id=data['grantee_id'],
                document_id=data['document_id'],
                access_level=access_level,
                expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
                granted_by=str(current_user['_id']),
                reason=data.get('reason', '')
            )
            
            grant_id = db_manager.insert_one('access_grants', access_grant.__dict__)
            success = bool(grant_id)
            action = 'ACCESS_GRANTED'

        if success:
            # Log access grant
            AuditLogger.log_access_grant(
                grantor_id=str(current_user['_id']),
                grantee_id=data['grantee_id'],
                document_id=data['document_id'],
                action=action
            )

            return jsonify({
                'message': 'Access granted successfully',
                'grant_id': grant_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 201 if action == 'ACCESS_GRANTED' else 200
        else:
            return jsonify({
                'error': {
                    'code': 'GRANT_FAILED',
                    'message': 'Failed to grant access',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 500

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'ACCESS_GRANT_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@access_bp.route('/revoke/<grant_id>', methods=['DELETE'])
@require_auth
def revoke_access(grant_id):
    """Revoke access to a medical document"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 401

        # Find the access grant
        access_grant = db_manager.find_one('access_grants', {
            '_id': ObjectId(grant_id),
            'is_active': True
        })
        
        if not access_grant:
            return jsonify({
                'error': {
                    'code': 'GRANT_NOT_FOUND',
                    'message': 'Access grant not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404

        # Check if current user can revoke access
        can_revoke = False
        
        # Grantor can revoke access they granted
        if str(current_user['_id']) == access_grant['grantor_id']:
            can_revoke = True
        
        # Admin can revoke any access
        elif current_user['role'] == UserRole.ADMIN.value:
            can_revoke = True
        
        # Grantee can revoke their own access
        elif str(current_user['_id']) == access_grant['grantee_id']:
            can_revoke = True

        if not can_revoke:
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'You do not have permission to revoke this access grant',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 403

        # Revoke access (soft delete)
        success = db_manager.update_one(
            'access_grants',
            {'_id': ObjectId(grant_id)},
            {'is_active': False}
        )

        if success:
            # Log access revocation
            AuditLogger.log_access_grant(
                grantor_id=str(current_user['_id']),
                grantee_id=access_grant['grantee_id'],
                document_id=access_grant['document_id'],
                action='ACCESS_REVOKED'
            )

            return jsonify({
                'message': 'Access revoked successfully',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'error': {
                    'code': 'REVOKE_FAILED',
                    'message': 'Failed to revoke access',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 500

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'ACCESS_REVOKE_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@access_bp.route('/grants/<document_id>', methods=['GET'])
@require_auth
def get_access_grants(document_id):
    """Get all access grants for a document"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'User not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 401

        # Find the document
        document = db_manager.find_one('medical_documents', {
            '_id': ObjectId(document_id),
            'is_deleted': False
        })
        
        if not document:
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_FOUND',
                    'message': 'Medical document not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404

        # Check if current user can view access grants
        can_view = False
        
        # Patient can view grants for their own records
        if (current_user['role'] == UserRole.PATIENT.value and 
            str(current_user['_id']) == document['patient_id']):
            can_view = True
        
        # Doctor can view grants for records they created
        elif (current_user['role'] == UserRole.DOCTOR.value and 
              str(current_user['_id']) == document['doctor_id']):
            can_view = True
        
        # Admin can view all grants
        elif current_user['role'] == UserRole.ADMIN.value:
            can_view = True

        if not can_view:
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'You do not have permission to view access grants for this document',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 403

        # Get access grants
        grants = db_manager.find_many('access_grants', {
            'document_id': document_id,
            'is_active': True
        })

        # Format grants with user information
        formatted_grants = []
        for grant in grants:
            # Get grantee information
            grantee = db_manager.find_one('users', {'_id': ObjectId(grant['grantee_id'])})
            
            grant_data = {
                'id': str(grant['_id']),
                'grantee': {
                    'id': grant['grantee_id'],
                    'name': f"{grantee['first_name']} {grantee['last_name']}" if grantee else 'Unknown User',
                    'email': grantee['email'] if grantee else 'Unknown',
                    'role': grantee['role'] if grantee else 'Unknown'
                },
                'access_level': grant['access_level'],
                'granted_at': grant['created_at'].isoformat(),
                'expires_at': grant['expires_at'].isoformat() if grant.get('expires_at') else None,
                'reason': grant.get('reason', ''),
                'granted_by': grant.get('granted_by')
            }
            
            formatted_grants.append(grant_data)

        return jsonify({
            'grants': formatted_grants,
            'count': len(formatted_grants),
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GRANTS_LIST_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500