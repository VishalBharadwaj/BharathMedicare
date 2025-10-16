// MongoDB initialization script for Medical Records System

// Switch to the medical_records database
db = db.getSiblingDB('medical_records');

// Create collections with validation
db.createCollection('users', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['email', 'password_hash', 'role', 'first_name', 'last_name'],
            properties: {
                email: {
                    bsonType: 'string',
                    pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                },
                role: {
                    bsonType: 'string',
                    enum: ['patient', 'doctor', 'admin']
                },
                is_active: {
                    bsonType: 'bool'
                }
            }
        }
    }
});

db.createCollection('medical_documents', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['patient_id', 'doctor_id', 'document_type', 'encrypted_content'],
            properties: {
                document_type: {
                    bsonType: 'string',
                    enum: ['lab_result', 'prescription', 'diagnosis', 'imaging', 'consultation']
                },
                is_deleted: {
                    bsonType: 'bool'
                }
            }
        }
    }
});

db.createCollection('access_grants', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['grantor_id', 'grantee_id', 'document_id', 'access_level'],
            properties: {
                access_level: {
                    bsonType: 'string',
                    enum: ['read', 'write', 'admin']
                },
                is_active: {
                    bsonType: 'bool'
                }
            }
        }
    }
});

db.createCollection('audit_logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['user_id', 'action', 'resource_type', 'resource_id'],
            properties: {
                success: {
                    bsonType: 'bool'
                }
            }
        }
    }
});

print('✅ Medical Records System database initialized successfully');
print('📊 Collections created: users, medical_documents, access_grants, audit_logs');
print('🔒 Validation rules applied for data integrity');