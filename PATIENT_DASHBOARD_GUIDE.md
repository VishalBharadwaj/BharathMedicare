# Patient Dashboard - Complete Guide

## Overview
The patient dashboard provides a comprehensive interface for patients to manage their medical records, control access, and maintain their profile.

## Features Implemented

### 1. Dashboard (Home)
**Location:** Main landing page after login

**Features:**
- **Statistics Cards:**
  - Total Records count
  - Healthcare Providers count
  - Active Access Grants count
  - Last Activity date
- **Recent Medical Records:** Shows the 5 most recent records
- **Quick Actions:** Easy navigation to other sections

**API Endpoints Used:**
- `GET /api/records/patient/{patient_id}` - Fetch patient records

### 2. My Records
**Location:** Records section in sidebar

**Features:**
- **View All Records:** Complete list of medical documents
- **Filter by Type:** Lab results, prescriptions, diagnosis, imaging, consultation notes
- **Filter by Date:** Last 7 days, 30 days, 3 months, year, or all time
- **Pagination:** Navigate through large record sets
- **Actions:**
  - View record details
  - Download encrypted records
  - Upload new documents

**API Endpoints Used:**
- `GET /api/records/patient/{patient_id}` - List records with filters
- `GET /api/records/{record_id}` - Get specific record
- `POST /api/records/upload` - Upload new record

### 3. Upload Documents
**Location:** Upload section in sidebar

**Features:**
- **Document Upload Form:**
  - Title (required)
  - Document Type (required): Lab results, prescription, diagnosis, imaging, consultation
  - Description (optional)
  - File upload (PDF, images, Word docs, max 16MB)
- **Security:**
  - AES-256 encryption before upload
  - Checksum verification
  - Secure storage in database
- **File Validation:**
  - Supported formats: PDF, JPG, PNG, DOC, DOCX
  - Maximum size: 16MB
  - MIME type verification

**API Endpoints Used:**
- `POST /api/records/upload` - Upload encrypted document

**Data Stored in Database:**
```json
{
  "patient_id": "user_id",
  "title": "Document title",
  "description": "Optional description",
  "document_type": "lab_result|prescription|diagnosis|imaging|consultation",
  "encrypted_content": "base64_encrypted_data",
  "encryption_iv": "initialization_vector",
  "file_size": 1234567,
  "mime_type": "application/pdf",
  "checksum": "sha256_hash",
  "created_at": "2024-01-01T00:00:00Z",
  "is_deleted": false
}
```

### 4. Access Control
**Location:** Access section in sidebar

**Features:**
- **Grant Access:**
  - Search for healthcare providers by name or email
  - Select specific document to share
  - Choose access level (Read Only or Read & Write)
  - Set expiration date (optional)
  - Provide reason for access
- **Active Access Grants:**
  - View all current access permissions
  - See who has access to which documents
  - Revoke access at any time
- **Access Audit:**
  - Track who accessed what and when
  - View access history

**API Endpoints Used:**
- `GET /api/users/search?role=doctor&q={query}` - Search doctors
- `POST /api/access/grant` - Grant access to document
- `GET /api/access/grants/{document_id}` - List access grants
- `DELETE /api/access/revoke/{grant_id}` - Revoke access

**Access Grant Data Structure:**
```json
{
  "document_id": "record_id",
  "patient_id": "patient_user_id",
  "grantee_id": "doctor_user_id",
  "access_level": "read|write",
  "expires_at": "2024-12-31T23:59:59Z",
  "reason": "Treatment consultation",
  "is_active": true,
  "granted_at": "2024-01-01T00:00:00Z"
}
```

### 5. Profile Management
**Location:** Profile section in sidebar

**Features:**
- **Personal Information:**
  - First Name
  - Last Name
  - Email (read-only for security)
  - Date of Birth
  - Emergency Contact Name
  - Emergency Contact Phone
- **Security Settings:**
  - Multi-Factor Authentication toggle
  - Password change
  - Login history viewer
- **Profile Updates:**
  - Real-time validation
  - Secure update process
  - Confirmation messages

**API Endpoints Used:**
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile

**Profile Data Structure:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "date_of_birth": "1990-01-01",
  "emergency_contact": {
    "name": "Jane Doe",
    "phone": "+1234567890",
    "relationship": "Spouse"
  },
  "insurance_info": {
    "provider": "Insurance Co",
    "policy_number": "POL123456"
  }
}
```

### 6. Medical History (Integrated)
**Location:** Available through Records section

**Features:**
- **Timeline View:** Chronological display of all medical records
- **Filter by Type:** View specific types of records
- **Search:** Find records by title or description
- **Export:** Download medical history as PDF (future feature)

## Technical Implementation

### Frontend Files
1. **`frontend/pages/patient-dashboard.html`** - Main dashboard HTML
2. **`frontend/js/patient-dashboard.js`** - Dashboard logic and API calls
3. **`frontend/js/api.js`** - API client for backend communication
4. **`frontend/js/ui.js`** - UI utilities and notifications
5. **`frontend/js/encryption.js`** - Client-side encryption
6. **`frontend/js/auth.js`** - Authentication management
7. **`frontend/js/config.js`** - API configuration

### Backend Endpoints Required
```
# Records Management
GET    /api/records/patient/{patient_id}     - List patient records
GET    /api/records/{record_id}              - Get specific record
POST   /api/records/upload                   - Upload new record
DELETE /api/records/{record_id}              - Delete record

# Access Control
POST   /api/access/grant                     - Grant access
GET    /api/access/grants/{document_id}      - List grants
DELETE /api/access/revoke/{grant_id}         - Revoke access

# User Management
GET    /api/users/profile                    - Get profile
PUT    /api/users/profile                    - Update profile
GET    /api/users/search                     - Search users

# Authentication
GET    /api/auth/me                          - Get current user
POST   /api/auth/refresh                     - Refresh token
```

## Security Features

### 1. Encryption
- **Client-Side Encryption:** Documents encrypted before upload using AES-256
- **Key Management:** Encryption keys stored securely
- **Checksum Verification:** SHA-256 checksums for data integrity

### 2. Access Control
- **Role-Based:** Patients can only access their own records
- **Time-Limited:** Access grants can have expiration dates
- **Audit Trail:** All access logged for compliance

### 3. Authentication
- **JWT Tokens:** Secure token-based authentication
- **Token Refresh:** Automatic token renewal
- **Session Management:** Secure session handling

## Usage Instructions

### For Patients

#### Uploading a Document
1. Click "Upload Document" in sidebar
2. Fill in document details:
   - Enter a descriptive title
   - Select document type
   - Add optional description
3. Choose file from computer
4. Click "Encrypt & Upload Document"
5. Wait for confirmation message

#### Granting Access to a Doctor
1. Click "Access Control" in sidebar
2. In "Grant Access" section:
   - Search for doctor by name
   - Select doctor from results
   - Choose which document to share
   - Select access level
   - Optionally set expiration date
   - Provide reason for access
3. Click "Grant Access"
4. View granted access in "Active Access Grants" section

#### Viewing Medical Records
1. Click "My Records" in sidebar
2. Use filters to narrow down records:
   - Filter by document type
   - Filter by date range
3. Click "View" on any record to see details
4. Click "Download" to save encrypted copy

#### Updating Profile
1. Click "Profile" in sidebar
2. Update personal information
3. Click "Update Profile"
4. Confirm changes saved

### For Developers

#### Adding New Document Types
Edit the document type options in:
- `frontend/pages/patient-dashboard.html` (upload form and filters)
- Backend validation in `backend/app/blueprints/records.py`

#### Customizing Encryption
Modify encryption settings in:
- `frontend/js/encryption.js`
- Backend decryption in `backend/app/utils/encryption.py`

#### Adding New Features
1. Add UI elements to `patient-dashboard.html`
2. Add JavaScript logic to `patient-dashboard.js`
3. Create backend endpoints in appropriate blueprint
4. Update API client in `api.js`

## Testing

### Manual Testing Checklist
- [ ] Login as patient
- [ ] View dashboard statistics
- [ ] Upload a document
- [ ] View uploaded document
- [ ] Download document
- [ ] Search for a doctor
- [ ] Grant access to doctor
- [ ] View active access grants
- [ ] Update profile information
- [ ] Filter records by type
- [ ] Filter records by date
- [ ] Navigate between sections
- [ ] Logout

### API Testing
```bash
# Get patient records
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/records/patient/PATIENT_ID

# Upload document
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","document_type":"lab_result",...}' \
  http://localhost:5000/api/records/upload

# Grant access
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_id":"DOC_ID","grantee_id":"DOCTOR_ID",...}' \
  http://localhost:5000/api/access/grant
```

## Troubleshooting

### Common Issues

**Records not loading:**
- Check browser console for errors
- Verify backend is running
- Confirm patient is logged in
- Check API endpoint URLs

**Upload failing:**
- Verify file size < 16MB
- Check file format is supported
- Ensure encryption.js is loaded
- Check network tab for errors

**Access grant not working:**
- Verify doctor exists in system
- Check document ID is valid
- Ensure access endpoint is available
- Review backend logs

**Profile not updating:**
- Check form validation
- Verify all required fields filled
- Check API response in network tab
- Review backend validation rules

## Future Enhancements

1. **Medical History Timeline:** Visual timeline of all medical events
2. **Export to PDF:** Download complete medical history
3. **Appointment Scheduling:** Book appointments with doctors
4. **Medication Reminders:** Set reminders for prescriptions
5. **Health Metrics:** Track vitals and health indicators
6. **Telemedicine:** Video consultations with doctors
7. **Family Sharing:** Share records with family members
8. **Insurance Integration:** Direct insurance claims
9. **Lab Results Notifications:** Alerts for new results
10. **Document Scanning:** Mobile app for scanning documents

## Support

For issues or questions:
1. Check browser console for errors
2. Review backend logs
3. Verify API endpoints are accessible
4. Check authentication token is valid
5. Ensure database connections are working
