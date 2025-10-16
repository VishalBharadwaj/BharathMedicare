# Medical Records Management System

A secure, HIPAA-compliant web application for managing patient medical records with end-to-end encryption, role-based access control, and comprehensive audit logging.

## 🚀 Features

### Security & Compliance
- **AES-256 Client-Side Encryption**: All medical data is encrypted before transmission
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Multi-Factor Authentication**: TOTP-based 2FA for enhanced security
- **Role-Based Access Control**: Granular permissions for Patients, Doctors, and Administrators
- **Audit Logging**: Complete trail of all access and modifications
- **HIPAA Compliance**: Designed to meet healthcare data protection standards

### Technical Features
- **Modern Architecture**: Flask backend with MongoDB and Redis
- **Responsive Frontend**: Clean, accessible HTML/CSS/JavaScript interface
- **Real-time Encryption**: Client-side encryption ensures data privacy
- **Scalable Design**: Modular blueprint architecture for easy expansion
- **Comprehensive Testing**: Unit tests for critical functionality

## 📁 Project Structure

```
medical-records-system/
├── backend/                    # Flask backend application
│   ├── app/
│   │   ├── blueprints/        # API route blueprints
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── records.py     # Medical records management
│   │   │   ├── users.py       # User management
│   │   │   └── access.py      # Access control
│   │   ├── models/            # Data models and schemas
│   │   │   ├── database.py    # Database manager
│   │   │   └── schemas.py     # Data schemas
│   │   └── utils/             # Utility modules
│   │       ├── auth.py        # Authentication utilities
│   │       ├── audit.py       # Audit logging
│   │       └── encryption.py  # Server-side encryption
│   ├── config/
│   │   └── settings.py        # Application configuration
│   ├── tests/                 # Unit tests
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Application entry point
├── frontend/                  # Frontend web application
│   ├── pages/                 # HTML pages
│   │   ├── login.html
│   │   ├── register.html
│   │   └── patient-dashboard.html
│   ├── js/                    # JavaScript modules
│   │   ├── auth.js           # Authentication manager
│   │   ├── api.js            # API client
│   │   ├── encryption.js     # Client-side encryption
│   │   ├── ui.js             # UI utilities
│   │   └── patient-dashboard.js
│   ├── assets/css/           # Stylesheets
│   └── index.html            # Landing page
├── setup.py                  # Automated setup script
└── README.md                 # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+**
- **MongoDB 4.4+**
- **Redis 6.0+**
- **Git**

### Automated Setup

Run the automated setup script:

```bash
python setup.py
```

This will:
- Check system requirements
- Install Python dependencies
- Create necessary directories
- Set up environment configuration
- Verify database connections

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd medical-records-system
   ```

2. **Check requirements**
   ```bash
   python check_requirements.py
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Test imports (optional)**
   ```bash
   cd backend
   python test_imports.py
   ```

5. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

6. **Start required services**
   ```bash
   # Start MongoDB (varies by OS)
   sudo systemctl start mongod  # Linux
   brew services start mongodb  # macOS
   
   # Start Redis
   sudo systemctl start redis   # Linux
   brew services start redis    # macOS
   ```

7. **Run the application**
   ```bash
   cd backend
   python run.py
   ```

## ⚙️ Configuration

### Environment Variables

Edit `backend/.env` with your configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
FLASK_ENV=development

# JWT Configuration
JWT_SECRET_KEY=jwt-secret-change-in-production

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/medical_records
MONGODB_DB=medical_records
REDIS_URL=redis://localhost:6379/0

# Security Configuration
BCRYPT_LOG_ROUNDS=12

# CORS Configuration
CORS_ORIGINS=https://localhost:3000,http://localhost:3000
```

### Database Setup

The application will automatically create necessary database indexes on startup. No manual database setup is required.

## 🚀 Usage

### User Roles

1. **Patients**
   - Upload and manage personal medical records
   - Grant access to healthcare providers
   - View audit logs of record access

2. **Doctors**
   - Access patient records (with permission)
   - Upload medical documents for patients
   - Manage patient care documentation

3. **Administrators**
   - Manage user accounts
   - System configuration
   - Audit trail monitoring

### Getting Started

1. **Access the application**: Open `http://localhost:5000` in your browser
2. **Register an account**: Click "Register" and create your account
3. **Login**: Use your credentials to access the dashboard
4. **Upload records**: Use the upload feature to add medical documents
5. **Manage access**: Grant healthcare providers access to specific records

## 🔒 Security Features

### Encryption
- **Client-Side**: AES-256-GCM encryption before data leaves the browser
- **Transport**: HTTPS/TLS 1.3 for all communications
- **Storage**: Encrypted data storage with separate key management

### Authentication
- **JWT Tokens**: Secure, stateless authentication
- **Refresh Tokens**: Automatic token renewal
- **MFA Support**: TOTP-based two-factor authentication
- **Session Management**: Secure session handling

### Access Control
- **Role-Based Permissions**: Granular access control
- **Document-Level Security**: Per-document access grants
- **Time-Based Access**: Expiring access permissions
- **Audit Trail**: Complete logging of all access

## 🧪 Testing

Run the test suite:

```bash
cd backend
python -m pytest tests/ -v
```

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/validate` - Token validation

### Records Endpoints
- `POST /api/records/upload` - Upload medical record
- `GET /api/records/{id}` - Get specific record
- `GET /api/records/patient/{id}` - List patient records

### User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/search` - Search users

### Access Control
- `POST /api/access/grant` - Grant record access
- `DELETE /api/access/revoke/{id}` - Revoke access
- `GET /api/access/grants/{document_id}` - List access grants

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use production-grade secrets
2. **Database**: Configure MongoDB replica sets for high availability
3. **Caching**: Configure Redis clustering for scalability
4. **SSL/TLS**: Use proper SSL certificates
5. **Monitoring**: Implement logging and monitoring solutions

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the test files for usage examples

## 🔮 Roadmap

- [ ] Mobile application (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with EHR systems
- [ ] Blockchain-based audit trail
- [ ] AI-powered document classification
- [ ] Telemedicine integration

---

**⚠️ Important**: This system handles sensitive medical data. Ensure proper security measures, regular updates, and compliance with local healthcare regulations before production use.
- JWT with multi-factor authentication
- RBAC on all endpoints
- Audit logging
- HTTPS enforcement
- Input validation and sanitization