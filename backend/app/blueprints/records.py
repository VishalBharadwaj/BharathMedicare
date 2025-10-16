from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import MedicalDocumentSchema, DocumentType, UserRole
from app.utils.auth import require_auth, require_role, get_current_user
from app.utils.audit import AuditLogger
from app.utils.encryption import EncryptionManager, KeyManager
import uuid
import base64

records_bp = Blueprint('records', __name__)

@records_bp.route('/upload', methods=['POST'])
@require_role(UserRole.DOCTOR, UserRole.PATIENT)
def upload_record(current_user):
    """Upload a new medical record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'document_type', 'encrypted_content', 'title']
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
        
        # Validate document type
        try:
            doc_type = DocumentType(data['document_type'])
        except ValueError:
            return jsonify({
                'error': {
                    'code': 'INVALID_DOCUMENT_TYPE',
                    'message': f'Invalid document type: {data["document_type"]}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 400
        
        # Verify patient exists
        patient = db_manager.find_one('users', {
            '_id': ObjectId(data['patient_id']),
            'role': UserRole.PATIENT.value
        })
        if not patient:
            return jsonify({
                'error': {
                    'code': 'PATIENT_NOT_FOUND',
                    'message': 'Patient not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404
        
        # Check permissions (patients can only upload their own records)
        if current_user['role'] == UserRole.PATIENT.value:
            if str(current_user['_id']) != data['patient_id']:
                return jsonify({
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': 'Patients can only upload their own records',
                        'timestamp': datetime.utcnow().isoformat(),
                        'requestId': str(uuid.uuid4())
                    }
                }), 403
        
        # Generate encryption key for this document
        key_data = KeyManager.generate_document_key()
        KeyManager.store_key(key_data, current_user['_id'])
        
        # Calculate checksum of encrypted content
        checksum = EncryptionManager.calculate_checksum(data['encrypted_content'])
        
        # Create medical document
        document = MedicalDocumentSchema(
            patient_id=data['patient_id'],
            doctor_id=str(current_user['_id']),
            document_type=doc_type,
            encrypted_content=data['encrypted_content'],
            encryption_key_id=key_data['key_id'],
            title=data['title'],
            description=data.get('description', ''),
            file_size=data.get('file_size', 0),
            mime_type=data.get('mime_type', 'application/octet-stream'),
            checksum=checksum
        )
        
        # Insert document
        document_id = db_manager.insert_one('medical_documents', document.__dict__)
        
        # Log document upload
        AuditLogger.log_document_access(
            user_id=str(current_user['_id']),
            document_id=document_id,
            action='DOCUMENT_UPLOADED'
        )
        
        return jsonify({
            'message': 'Medical record uploaded successfully',
            'document_id': document_id,
            'timestamp': datetime.utcnow().isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'UPLOAD_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500
@records_bp.route('/<document_id>', methods=['GET'])

@require_auth
def get_record(document_id):
    """Get a specific medical record"""
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
        
        # Find document
        document = db_manager.find_one('medical_documents', {
            '_id': ObjectId(document_id),
            'is_deleted': False
        })
        
        if not document:
            return jsonify({
                'error': {
                    'code': 'DOCUMENT_NOT_FOUND',
                    'message': 'Medical record not found',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 404
        
        # Check access permissions
        has_access = False
        
        # Patient can access their own records
        if (current_user['role'] == UserRole.PATIENT.value and 
            str(current_user['_id']) == document['patient_id']):
            has_access = True
        
        # Doctor can access records they created
        elif (current_user['role'] == UserRole.DOCTOR.value and 
              str(current_user['_id']) == document['doctor_id']):
            has_access = True
        
        # Admin can access all records
        elif current_user['role'] == UserRole.ADMIN.value:
            has_access = True
        
        # Check for explicit access grants
        else:
            access_grant = db_manager.find_one('access_grants', {
                'grantee_id': str(current_user['_id']),
                'document_id': document_id,
                'is_active': True,
                '$or': [
                    {'expires_at': {'$gt': datetime.utcnow()}},
                    {'expires_at': None}
                ]
            })
            if access_grant:
                has_access = True
        
        if not has_access:
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Access denied to this medical record',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 403
        
        # Log document access
        AuditLogger.log_document_access(
            user_id=str(current_user['_id']),
            document_id=document_id,
            action='DOCUMENT_VIEWED'
        )
        
        # Return document (without decryption key for security)
        response_data = {
            'id': str(document['_id']),
            'patient_id': document['patient_id'],
            'doctor_id': document['doctor_id'],
            'document_type': document['document_type'],
            'title': document['title'],
            'description': document['description'],
            'encrypted_content': document['encrypted_content'],
            'encryption_key_id': document['encryption_key_id'],
            'file_size': document['file_size'],
            'mime_type': document['mime_type'],
            'checksum': document['checksum'],
            'created_at': document['created_at'].isoformat(),
            'updated_at': document['updated_at'].isoformat()
        }
        
        return jsonify({
            'document': response_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'RETRIEVAL_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@records_bp.route('/patient/<patient_id>', methods=['GET'])
@require_auth
def list_patient_records(patient_id):
    """List all records for a specific patient"""
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
        
        # Check access permissions
        has_access = False
        
        # Patient can access their own records
        if (current_user['role'] == UserRole.PATIENT.value and 
            str(current_user['_id']) == patient_id):
            has_access = True
        
        # Admin can access all records
        elif current_user['role'] == UserRole.ADMIN.value:
            has_access = True
        
        # Doctor can access if they have treated the patient
        elif current_user['role'] == UserRole.DOCTOR.value:
            doctor_records = db_manager.find_one('medical_documents', {
                'patient_id': patient_id,
                'doctor_id': str(current_user['_id']),
                'is_deleted': False
            })
            if doctor_records:
                has_access = True
        
        if not has_access:
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Access denied to patient records',
                    'timestamp': datetime.utcnow().isoformat(),
                    'requestId': str(uuid.uuid4())
                }
            }), 403
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Find documents
        documents = db_manager.find_many(
            'medical_documents',
            {'patient_id': patient_id, 'is_deleted': False},
            limit=limit,
            skip=skip,
            sort=[('created_at', -1)]
        )
        
        # Count total documents
        total_count = db_manager.count_documents(
            'medical_documents',
            {'patient_id': patient_id, 'is_deleted': False}
        )
        
        # Format response
        records = []
        for doc in documents:
            records.append({
                'id': str(doc['_id']),
                'document_type': doc['document_type'],
                'title': doc['title'],
                'description': doc['description'],
                'file_size': doc['file_size'],
                'mime_type': doc['mime_type'],
                'created_at': doc['created_at'].isoformat(),
                'doctor_id': doc['doctor_id']
            })
        
        # Log access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='PATIENT_RECORDS_LISTED',
            resource_type='PATIENT',
            resource_id=patient_id
        )
        
        return jsonify({
            'records': records,
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
                'code': 'LIST_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500