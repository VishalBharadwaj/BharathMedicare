from flask import current_app
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db = None
    
    def init_app(self, app):
        self.db = app.db
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance and uniqueness"""
        try:
            # Users collection indexes
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("role")
            self.db.users.create_index("is_active")
            
            # Medical documents indexes
            self.db.medical_documents.create_index("patient_id")
            self.db.medical_documents.create_index("doctor_id")
            self.db.medical_documents.create_index("document_type")
            self.db.medical_documents.create_index("created_at")
            self.db.medical_documents.create_index("is_deleted")
            
            # Access grants indexes
            self.db.access_grants.create_index([("grantee_id", 1), ("document_id", 1)])
            self.db.access_grants.create_index("grantor_id")
            self.db.access_grants.create_index("expires_at")
            self.db.access_grants.create_index("is_active")
            
            # Audit logs indexes
            self.db.audit_logs.create_index("user_id")
            self.db.audit_logs.create_index("created_at")
            self.db.audit_logs.create_index("action")
            self.db.audit_logs.create_index("resource_type")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating database indexes: {e}")

    def insert_one(self, collection: str, document: dict) -> str:
        """Insert a single document and return its ID"""
        try:
            result = self.db[collection].insert_one(document)
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error in {collection}: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise

    def find_one(self, collection: str, filter_dict: dict) -> dict:
        """Find a single document"""
        try:
            return self.db[collection].find_one(filter_dict)
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise

    def find_many(self, collection: str, filter_dict: dict, 
                  limit: int = None, skip: int = None, sort: list = None, projection: dict = None) -> list:
        """Find multiple documents with pagination"""
        try:
            cursor = self.db[collection].find(filter_dict, projection)
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise 
    def update_one(self, collection: str, filter_dict: dict, update_dict: dict) -> bool:
        """Update a single document"""
        try:
            update_dict['updated_at'] = datetime.utcnow()
            result = self.db[collection].update_one(filter_dict, {'$set': update_dict})
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise

    def delete_one(self, collection: str, filter_dict: dict) -> bool:
        """Delete a single document"""
        try:
            result = self.db[collection].delete_one(filter_dict)
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise

    def count_documents(self, collection: str, filter_dict: dict) -> int:
        """Count documents matching filter"""
        try:
            return self.db[collection].count_documents(filter_dict)
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise

    def aggregate(self, collection: str, pipeline: list) -> list:
        """Execute aggregation pipeline"""
        try:
            return list(self.db[collection].aggregate(pipeline))
        except PyMongoError as e:
            logger.error(f"Database error in {collection}: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()