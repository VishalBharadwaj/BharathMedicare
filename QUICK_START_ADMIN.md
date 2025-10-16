# Quick Start - Admin Dashboard

## ✅ What's Ready

1. **Admin Dashboard UI** - `frontend/pages/admin-dashboard.html`
2. **Admin API Endpoints** - `backend/app/blueprints/admin.py`
3. **Routes Registered** - All admin endpoints are live

## 🚀 How to Use

### Step 1: Restart Backend Server
The backend needs to be restarted to load the new admin blueprint:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python start-dev.py
```

### Step 2: Login as Admin
1. Open browser to `http://localhost:3000`
2. Login with admin credentials
3. You'll be automatically redirected to `http://localhost:3000/pages/admin-dashboard.html`

### Step 3: View Dashboard
You'll see:
- **Statistics Cards**: Total doctors, patients, records, and access grants
- **Doctors Tab**: List of all doctors with their details
- **Patients Tab**: List of all patients with their details
- **Search**: Filter doctors or patients by name/email

## 📊 Admin Dashboard Features

### Statistics Overview
- Real-time counts of system entities
- Updates on page load
- Color-coded cards for easy reading

### Doctors Management
- View all doctors
- See specialization, department, license number
- Search by name or email
- Active status indicators

### Patients Management  
- View all patients
- See date of birth, medical record number
- Search by name or email
- View detailed patient information
- Access patient records

## 🔐 API Endpoints Available

```
GET  /api/admin/statistics              - System statistics
GET  /api/admin/users                   - List all users
GET  /api/admin/users/<id>              - Get user details
POST /api/admin/users/<id>/toggle-status - Activate/deactivate user
```

All require admin authentication.

## 🧪 Test the Setup

### Test Statistics Endpoint
```bash
# First, get an admin token by logging in
# Then test:
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  http://localhost:5000/api/admin/statistics
```

Expected response:
```json
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

## 🎯 Key Differences from Doctor Dashboard

| Feature | Doctor Dashboard | Admin Dashboard |
|---------|-----------------|-----------------|
| Statistics | ❌ No | ✅ Yes (4 cards) |
| View Doctors | ❌ No | ✅ Yes |
| View Patients | ✅ Yes | ✅ Yes |
| User Management | ❌ No | ✅ Yes (future) |
| System Overview | ❌ No | ✅ Yes |

## 📝 Notes

- Admin dashboard uses the same config.js for API calls
- All routes use trailing slashes where needed (learned from patients fix!)
- Statistics are fetched from dedicated endpoint
- Search is client-side for better performance
- Responsive design works on mobile/tablet

## 🐛 Troubleshooting

### Dashboard not loading?
1. Hard refresh browser (Ctrl+Shift+R)
2. Check browser console for errors
3. Verify you're logged in as admin
4. Check backend is running on port 5000

### Statistics showing "-"?
1. Backend might not be restarted
2. Check admin token is valid
3. Verify admin blueprint is registered
4. Check browser network tab for API errors

### "Access Denied" error?
- You must be logged in as an admin user
- Check user role in localStorage: `localStorage.getItem('medical_user_data')`

## ✨ What's Next?

Future enhancements you could add:
- User activation/deactivation buttons
- Create new users from admin panel
- Edit user details
- View audit logs
- System health monitoring
- Export data to CSV
- Advanced filtering and sorting
- Charts and graphs for statistics
