from datetime import datetime
from flask import request
from app.models.database import db_manager
from app.models.schemas import AuditLogSchema
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    def log_action(user_id: str, action: str, resource_type: str, 
                   resource_id: str, success: bool = True, 
                   error_message: str = None, details: dict = None):
        """Log user action for audit trail"""
        try:
            audit_log = AuditLogSchema(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                success=success,
                error_message=error_message,
                details=details or {}
            ).__dict__
            
            db_manager.insert_one('audit_logs', audit_log)
            logger.info(f"Audit log created: {action} on {resource_type}:{resource_id} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    @staticmethod
    def log_login_attempt(user_id: str, success: bool, error_message: str = None):
        """Log login attempt"""
        AuditLogger.log_action(
            user_id=user_id,
            action='LOGIN_ATTEMPT',
            resource_type='USER',
            resource_id=user_id,
            success=success,
            error_message=error_message
        )
    
    @staticmethod
    def log_document_access(user_id: str, document_id: str, action: str):
        """Log document access"""
        AuditLogger.log_action(
            user_id=user_id,
            action=action,
            resource_type='MEDICAL_DOCUMENT',
            resource_id=document_id
        )
    
    @staticmethod
    def log_access_grant(grantor_id: str, grantee_id: str, document_id: str, action: str):
        """Log access grant changes"""
        AuditLogger.log_action(
            user_id=grantor_id,
            action=action,
            resource_type='ACCESS_GRANT',
            resource_id=document_id,
            details={'grantee_id': grantee_id}
        )
    
    @staticmethod
    def log_admin_action(admin_id: str, action: str, target_user_id: str = None, details: dict = None):
        """Log administrative actions"""
        AuditLogger.log_action(
            user_id=admin_id,
            action=action,
            resource_type='ADMIN_ACTION',
            resource_id=target_user_id or admin_id,
            details=details
        )