from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class UserRole(Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class DocumentType(Enum):
    LAB_RESULT = "lab_result"
    PRESCRIPTION = "prescription"
    DIAGNOSIS = "diagnosis"
    IMAGING = "imaging"
    CONSULTATION = "consultation"

class AccessLevel(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

# MongoDB Schema Definitions (Mongoose-style)
class BaseSchema:
    def __init__(self):
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class UserSchema(BaseSchema):
    def __init__(self, email: str, password_hash: str, role: UserRole, 
                 first_name: str, last_name: str, **kwargs):
        super().__init__()
        self.email = email
        self.password_hash = password_hash
        self.role = role.value
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = kwargs.get('is_active', True)
        self.mfa_enabled = kwargs.get('mfa_enabled', False)
        self.mfa_secret = kwargs.get('mfa_secret', None)
        self.last_login = kwargs.get('last_login', None)
        self.profile = kwargs.get('profile', {})

class PatientSchema(UserSchema):
    def __init__(self, **kwargs):
        super().__init__(role=UserRole.PATIENT, **kwargs)
        self.date_of_birth = kwargs.get('date_of_birth')
        self.medical_record_number = kwargs.get('medical_record_number')
        self.emergency_contact = kwargs.get('emergency_contact', {})
        self.insurance_info = kwargs.get('insurance_info', {})

class DoctorSchema(UserSchema):
    def __init__(self, **kwargs):
        super().__init__(role=UserRole.DOCTOR, **kwargs)
        self.license_number = kwargs.get('license_number')
        self.specialization = kwargs.get('specialization')
        self.department = kwargs.get('department')
        self.hospital_id = kwargs.get('hospital_id')

class AdminSchema(UserSchema):
    def __init__(self, **kwargs):
        super().__init__(role=UserRole.ADMIN, **kwargs)
        self.admin_level = kwargs.get('admin_level', 1)
        self.permissions = kwargs.get('permissions', [])

class MedicalDocumentSchema(BaseSchema):
    def __init__(self, patient_id: str, doctor_id: str, document_type: DocumentType,
                 encrypted_content: str, encryption_key_id: str, **kwargs):
        super().__init__()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.document_type = document_type.value
        self.encrypted_content = encrypted_content
        self.encryption_key_id = encryption_key_id
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.file_size = kwargs.get('file_size', 0)
        self.mime_type = kwargs.get('mime_type', '')
        self.checksum = kwargs.get('checksum', '')
        self.is_deleted = kwargs.get('is_deleted', False)
        self.retention_date = kwargs.get('retention_date')

class AccessGrantSchema(BaseSchema):
    def __init__(self, grantor_id: str, grantee_id: str, document_id: str,
                 access_level: AccessLevel, **kwargs):
        super().__init__()
        self.grantor_id = grantor_id
        self.grantee_id = grantee_id
        self.document_id = document_id
        self.access_level = access_level.value
        self.expires_at = kwargs.get('expires_at')
        self.is_active = kwargs.get('is_active', True)
        self.granted_by = kwargs.get('granted_by')
        self.reason = kwargs.get('reason', '')

class AuditLogSchema(BaseSchema):
    def __init__(self, user_id: str, action: str, resource_type: str,
                 resource_id: str, **kwargs):
        super().__init__()
        self.user_id = user_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
        self.details = kwargs.get('details', {})
        self.success = kwargs.get('success', True)
        self.error_message = kwargs.get('error_message')