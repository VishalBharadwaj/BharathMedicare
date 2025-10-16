from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from app.models.database import db_manager
from app.models.schemas import UserRole
from app.utils.auth import require_auth, require_role, get_current_user
from app.utils.audit import AuditLogger
import uuid

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'message': 'Patients API is working',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@patients_bp.route('/', methods=['GET'])
@require_role(UserRole.DOCTOR, UserRole.ADMIN)
def list_patients(current_user):
    """List all patients accessible to the current doctor/admin"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        
        # Build query based on user role
        # Both doctors and admins can see all patients (this is typical in medical systems)
        # Access control is handled at the record level, not patient level
        query = {'role': UserRole.PATIENT.value, 'is_active': True}
        
        # Find patients
        patients = db_manager.find_many(
            'users',
            query,
            limit=limit,
            skip=skip,
            sort=[('last_name', 1), ('first_name', 1)]
        )
        
        # Count total patients
        total_count = db_manager.count_documents('users', query)
        
        # Format response (remove sensitive information)
        patient_list = []
        for patient in patients:
            patient_data = {
                'id': str(patient['_id']),
                '_id': str(patient['_id']),  # Include both for compatibility
                'first_name': patient['first_name'],
                'last_name': patient['last_name'],
                'email': patient['email'],
                'date_of_birth': patient.get('date_of_birth'),
                'medical_record_number': patient.get('medical_record_number'),
                'created_at': patient['created_at'].isoformat(),
                'last_login': patient.get('last_login').isoformat() if patient.get('last_login') else None
            }
            
            # Add emergency contact if available (for doctors/admins)
            if patient.get('emergency_contact'):
                patient_data['emergency_contact'] = patient['emergency_contact']
            
            patient_list.append(patient_data)
        
        # Log access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='PATIENTS_LISTED',
            resource_type='PATIENT',
            resource_id='multiple',
            details={'count': len(patient_list)}
        )
        
        return jsonify({
            'patients': patient_list,
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
                'code': 'LIST_PATIENTS_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@patients_bp.route('/<patient_id>', methods=['GET'])
@require_role(UserRole.DOCTOR, UserRole.ADMIN)
def get_patient(patient_id, current_user):
    """Get detailed information about a specific patient"""
    try:
        # Find patient
        patient = db_manager.find_one('users', {
            '_id': ObjectId(patient_id),
            'role': UserRole.PATIENT.value,
            'is_active': True
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
        
        # Doctors can access all patient basic information
        # Detailed medical records access is controlled at the records level
        # This allows doctors to see patient directory and request access to records
        
        # Format patient data
        patient_data = {
            'id': str(patient['_id']),
            '_id': str(patient['_id']),
            'first_name': patient['first_name'],
            'last_name': patient['last_name'],
            'email': patient['email'],
            'date_of_birth': patient.get('date_of_birth'),
            'medical_record_number': patient.get('medical_record_number'),
            'emergency_contact': patient.get('emergency_contact', {}),
            'insurance_info': patient.get('insurance_info', {}),
            'created_at': patient['created_at'].isoformat(),
            'last_login': patient.get('last_login').isoformat() if patient.get('last_login') else None
        }
        
        # Log access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='PATIENT_VIEWED',
            resource_type='PATIENT',
            resource_id=patient_id
        )
        
        return jsonify({
            'patient': patient_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_PATIENT_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500

@patients_bp.route('/search', methods=['GET'])
@require_role(UserRole.DOCTOR, UserRole.ADMIN)
def search_patients(current_user):
    """Search for patients by name, email, or medical record number"""
    try:
        query = request.args.get('q', '').strip()
        
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
                {'email': {'$regex': query, '$options': 'i'}},
                {'medical_record_number': {'$regex': query, '$options': 'i'}}
            ],
            'role': UserRole.PATIENT.value,
            'is_active': True
        }
        
        # Doctors can search all patients (access control is at record level)
        # This allows doctors to find patients and request access to their records
        
        # Find patients
        patients = db_manager.find_many('users', search_filter, limit=20)
        
        # Format results
        results = []
        for patient in patients:
            results.append({
                'id': str(patient['_id']),
                '_id': str(patient['_id']),
                'first_name': patient['first_name'],
                'last_name': patient['last_name'],
                'email': patient['email'],
                'medical_record_number': patient.get('medical_record_number'),
                'date_of_birth': patient.get('date_of_birth')
            })
        
        # Log search
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='PATIENTS_SEARCHED',
            resource_type='PATIENT',
            resource_id='multiple',
            details={'query': query, 'results_count': len(results)}
        )
        
        return jsonify({
            'patients': results,
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

@patients_bp.route('/<patient_id>/records', methods=['GET'])
@require_role(UserRole.DOCTOR, UserRole.ADMIN)
def get_patient_records(patient_id, current_user):
    """Get all medical records for a specific patient"""
    try:
        # Verify patient exists
        patient = db_manager.find_one('users', {
            '_id': ObjectId(patient_id),
            'role': UserRole.PATIENT.value,
            'is_active': True
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
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Find all medical records for this patient
        records_query = {'patient_id': patient_id, 'is_deleted': False}
        
        # For doctors, they can see records they created or have access to
        if current_user['role'] == UserRole.DOCTOR.value:
            doctor_id = str(current_user['_id'])
            
            # Find records the doctor created
            doctor_records = db_manager.find_many(
                'medical_documents',
                {'patient_id': patient_id, 'doctor_id': doctor_id, 'is_deleted': False},
                projection={'_id': 1}
            )
            
            # Find records the doctor has access to via grants
            access_grants = db_manager.find_many(
                'access_grants',
                {
                    'grantee_id': doctor_id,
                    'patient_id': patient_id,
                    'is_active': True,
                    '$or': [
                        {'expires_at': {'$gt': datetime.utcnow()}},
                        {'expires_at': None}
                    ]
                },
                projection={'document_id': 1}
            )
            
            # Collect accessible record IDs
            accessible_record_ids = [str(record['_id']) for record in doctor_records]
            for grant in access_grants:
                if grant.get('document_id') and grant['document_id'] not in accessible_record_ids:
                    accessible_record_ids.append(grant['document_id'])
            
            if accessible_record_ids:
                # Convert to ObjectIds
                object_ids = []
                for rid in accessible_record_ids:
                    try:
                        object_ids.append(ObjectId(rid))
                    except:
                        continue
                
                records_query['_id'] = {'$in': object_ids}
            else:
                # Doctor has no access to any records for this patient
                return jsonify({
                    'records': [],
                    'patient': {
                        'id': str(patient['_id']),
                        'first_name': patient['first_name'],
                        'last_name': patient['last_name'],
                        'medical_record_number': patient.get('medical_record_number')
                    },
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': 0,
                        'pages': 0
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }), 200
        
        # Find records
        records = db_manager.find_many(
            'medical_documents',
            records_query,
            limit=limit,
            skip=skip,
            sort=[('created_at', -1)]
        )
        
        # Count total records
        total_count = db_manager.count_documents('medical_documents', records_query)
        
        # Format records
        formatted_records = []
        for record in records:
            formatted_records.append({
                'id': str(record['_id']),
                'document_type': record['document_type'],
                'title': record['title'],
                'description': record['description'],
                'file_size': record['file_size'],
                'mime_type': record['mime_type'],
                'created_at': record['created_at'].isoformat(),
                'doctor_id': record['doctor_id'],
                'checksum': record['checksum']
            })
        
        # Log access
        AuditLogger.log_action(
            user_id=str(current_user['_id']),
            action='PATIENT_RECORDS_ACCESSED',
            resource_type='PATIENT',
            resource_id=patient_id,
            details={'records_count': len(formatted_records)}
        )
        
        return jsonify({
            'records': formatted_records,
            'patient': {
                'id': str(patient['_id']),
                'first_name': patient['first_name'],
                'last_name': patient['last_name'],
                'medical_record_number': patient.get('medical_record_number')
            },
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
                'code': 'GET_RECORDS_ERROR',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'requestId': str(uuid.uuid4())
            }
        }), 500