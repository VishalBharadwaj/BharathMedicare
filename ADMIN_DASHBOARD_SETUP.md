# Admin Dashboard Setup

## What Was Created

### 1. Frontend - Admin Dashboard
**File:** `frontend/pages/admin-dashboard.html`

Features:
- **Statistics Cards** showing:
  - Total Doctors
  - Total Patients  
  - Medical Records count
  - Active Access Grants
- **Tabbed Interface** with:
  - Doctors tab - List all doctors with specialization, department, license number
  - Patients tab - List all patients with DOB, medical record number
- **Search Functionality** for both doctors and patients
- **Responsive Design** with modern UI
- **Real-time Data** loaded from backend API

### 2. Backend - Admin API
**File:** `backend/app/blueprints/admin.py`

Endpoints:
- `GET /api/admin/statistics` - Get system-wide statistics
  - Counts: doctors, patients, records, access grants, total users, admins
- `GET /api/admin/users` - List all users with pagination and role filtering
- `GET /api/admin/users/<user_id>` - Get detailed user information
- `POST /api/admin/users/<user_id>/toggle-status` - Activate/deactivate users

All endpoints require ADMIN role authentication.

### 3. Configuration Updates
- **`backend/app/__init__.py`** - Registered admin blueprint at `/api/admin`
- **`frontend/js/config.js`** - Added ADMIN endpoint configuration
- **`frontend/index.html`** - Already had admin redirect (no changes needed)

## How to Use

### 1. Start the Backend
```bash
python start-dev.py
```
Or manually:
```bash
cd backend
python run.py
```

### 2. Access Admin Dashboard
1. Navigate to `http://localhost:3000`
2. Login with an admin account
3. You'll be automatically redirected to the admin dashboard

### 3. Admin Dashboard Features

#### Statistics Overview
- View real-time counts of doctors, patients, records, and access grants
- Statistics update on page load

#### Doctors Management
- View all doctors in the system
- See specialization, department, and license information
- Search doctors by name or email
- Filter and sort doctor list

#### Patients Management
- View all patients in the system
- See date of birth and medical record numbers
- Search patients by name or email
- View detailed patient information
- Access patient records

## API Endpoints

### Statistics
```bash
GET /api/admin/statistics
Authorization: Bearer <admin_token>

Response:
{
  "statistics": {
    "doctors": 5,
    "patients": 20,
    "records": 45,
    "access_grants": 12,
    "total_users": 26,
    "admins": 1
  }
}
```

### List Users
```bash
GET /api/admin/users?role=doctor&page=1&limit=50
Authorization: Bearer <admin_token>

Response:
{
  "users": [...],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 5,
    "pages": 1
  }
}
```

### Get User Details
```bash
GET /api/admin/users/<user_id>
Authorization: Bearer <admin_token>

Response:
{
  "user": {
    "id": "...",
    "email": "...",
    "first_name": "...",
    "last_name": "...",
    "role": "doctor",
    ...
  }
}
```

## Security Features

1. **Role-Based Access Control** - Only admins can access admin endpoints
2. **Audit Logging** - All admin actions are logged
3. **Self-Protection** - Admins cannot deactivate their own accounts
4. **JWT Authentication** - All requests require valid admin token

## Testing

### Test Admin Endpoints
```bash
# Get statistics
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:5000/api/admin/statistics

# List all doctors
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:5000/api/admin/users?role=doctor

# List all patients  
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:5000/api/admin/users?role=patient
```

### Create Test Admin User
If you don't have an admin user, you can create one via the registration endpoint or directly in the database.

## Next Steps

1. **Restart Backend** - Restart the backend server to load the new admin blueprint
2. **Hard Refresh Browser** - Clear cache with Ctrl+Shift+R
3. **Login as Admin** - Use admin credentials to access the dashboard
4. **Verify Statistics** - Check that all counts are displaying correctly

## Files Modified/Created

### Created:
- `frontend/pages/admin-dashboard.html` - Admin dashboard UI
- `backend/app/blueprints/admin.py` - Admin API endpoints
- `ADMIN_DASHBOARD_SETUP.md` - This documentation

### Modified:
- `backend/app/__init__.py` - Registered admin blueprint
- `frontend/js/config.js` - Added admin endpoint configuration

## Notes

- The admin dashboard uses the same styling as doctor/patient dashboards for consistency
- All API calls use the centralized config for the backend URL
- Statistics are loaded on page load and can be refreshed manually
- Search is client-side for better performance with small datasets
- Pagination is supported but not yet implemented in the UI (can be added later)
