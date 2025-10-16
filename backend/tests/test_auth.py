import pytest
import json
from datetime import datetime
from backend.app import create_app
from backend.app.models.database import db_manager

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        # Initialize test database
        db_manager.init_app(app)
        yield app
        # Cleanup after tests
        app.db.users.delete_many({})
        app.db.medical_documents.delete_many({})
        app.db.access_grants.delete_many({})
        app.db.audit_logs.delete_many({})

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_patient_success(self, client):
        """Test successful patient registration"""
        user_data = {
            'email': 'patient@test.com',
            'password': 'testpassword123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'patient',
            'date_of_birth': '1990-01-01',
            'emergency_contact': {
                'name': 'Jane Doe',
                'phone': '555-0123'
            }
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert data['message'] == 'User registered successfully'
    
    def test_register_doctor_success(self, client):
        """Test successful doctor registration"""
        user_data = {
            'email': 'doctor@test.com',
            'password': 'testpassword123',
            'first_name': 'Dr. Jane',
            'last_name': 'Smith',
            'role': 'doctor',
            'license_number': 'MD123456',
            'specialization': 'Cardiology',
            'department': 'Cardiology Department'
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        user_data = {
            'email': 'test@test.com',
            'password': 'testpassword123'
            # Missing first_name, last_name, role
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Missing required field' in data['error']['message']
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        user_data = {
            'email': 'duplicate@test.com',
            'password': 'testpassword123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'patient'
        }
        
        # First registration
        response1 = client.post('/api/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = client.post('/api/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')
        assert response2.status_code == 409
        data = json.loads(response2.data)
        assert data['error']['code'] == 'USER_EXISTS'
    
    def test_login_success(self, client):
        """Test successful login"""
        # First register a user
        user_data = {
            'email': 'login@test.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'patient'
        }
        
        client.post('/api/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Then login
        login_data = {
            'email': 'login@test.com',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'login@test.com'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error']['code'] == 'INVALID_CREDENTIALS'
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        login_data = {
            'email': 'test@test.com'
            # Missing password
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Email and password are required' in data['error']['message']
    
    def test_validate_token_without_token(self, client):
        """Test token validation without providing token"""
        response = client.get('/api/auth/validate')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

class TestAuthorization:
    """Test authorization and role-based access control"""
    
    def get_auth_headers(self, client, email, password):
        """Helper method to get authentication headers"""
        login_data = {
            'email': email,
            'password': password
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            return {'Authorization': f'Bearer {data["access_token"]}'}
        return {}
    
    def test_role_based_access_patient(self, client):
        """Test patient role access"""
        # Register patient
        user_data = {
            'email': 'patient_role@test.com',
            'password': 'testpassword123',
            'first_name': 'Patient',
            'last_name': 'User',
            'role': 'patient'
        }
        
        client.post('/api/auth/register',
                   data=json.dumps(user_data),
                   content_type='application/json')
        
        # Get auth headers
        headers = self.get_auth_headers(client, 'patient_role@test.com', 'testpassword123')
        
        # Test access to user profile (should work)
        response = client.get('/api/users/profile', headers=headers)
        assert response.status_code == 200
    
    def test_unauthorized_access(self, client):
        """Test access without authentication"""
        response = client.get('/api/users/profile')
        assert response.status_code == 401