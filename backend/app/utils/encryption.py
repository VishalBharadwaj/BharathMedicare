from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import hashlib
import secrets

class EncryptionManager:
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """Encrypt data using Fernet (AES-256)"""
        f = Fernet(key.encode())
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """Decrypt data using Fernet (AES-256)"""
        f = Fernet(key.encode())
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = f.decrypt(decoded_data)
        return decrypted_data.decode()
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt"""
        return base64.urlsafe_b64encode(os.urandom(16)).decode()
    
    @staticmethod
    def calculate_checksum(data: str) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)

class KeyManager:
    """Manages encryption keys for medical documents"""
    
    @staticmethod
    def generate_document_key() -> dict:
        """Generate a new document encryption key with metadata"""
        key = EncryptionManager.generate_key()
        key_id = EncryptionManager.generate_secure_token(16)
        
        return {
            'key_id': key_id,
            'key': key,
            'created_at': datetime.utcnow(),
            'algorithm': 'AES-256-CBC',
            'key_length': 256
        }
    
    @staticmethod
    def store_key(key_data: dict, user_id: str):
        """Store encryption key securely (in production, use HSM or key vault)"""
        # In production, this should use a Hardware Security Module (HSM)
        # or cloud key management service like AWS KMS, Azure Key Vault, etc.
        from backend.app.models.database import db_manager
        
        key_record = {
            'key_id': key_data['key_id'],
            'encrypted_key': key_data['key'],  # Should be encrypted with master key
            'owner_id': user_id,
            'created_at': key_data['created_at'],
            'algorithm': key_data['algorithm'],
            'is_active': True
        }
        
        return db_manager.insert_one('encryption_keys', key_record)
    
    @staticmethod
    def get_key(key_id: str, user_id: str) -> str:
        """Retrieve encryption key by ID"""
        from backend.app.models.database import db_manager
        
        key_record = db_manager.find_one('encryption_keys', {
            'key_id': key_id,
            'owner_id': user_id,
            'is_active': True
        })
        
        if key_record:
            return key_record['encrypted_key']  # Should be decrypted with master key
        return None