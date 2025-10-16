#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all module imports"""
    try:
        print("Testing imports...")
        
        # Test basic Flask imports
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test app creation
        from app import create_app
        print("✅ App factory imported successfully")
        
        # Test database manager
        from app.models.database import db_manager
        print("✅ Database manager imported successfully")
        
        # Test schemas
        from app.models.schemas import UserRole, DocumentType, AccessLevel
        from app.models.schemas import UserSchema, PatientSchema, DoctorSchema, AdminSchema
        from app.models.schemas import MedicalDocumentSchema, AccessGrantSchema, AuditLogSchema
        print("✅ All schemas imported successfully")
        
        # Test utilities
        from app.utils.auth import AuthManager, require_auth, get_current_user
        from app.utils.audit import AuditLogger
        from app.utils.encryption import EncryptionManager, KeyManager
        print("✅ All utilities imported successfully")
        
        # Test blueprints
        from app.blueprints.auth import auth_bp
        from app.blueprints.users import users_bp
        from app.blueprints.records import records_bp
        from app.blueprints.access import access_bp
        print("✅ All blueprints imported successfully")
        
        print("\n🎉 All imports successful! The application should run correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_imports()
    exit(0 if success else 1)