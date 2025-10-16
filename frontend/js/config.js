/**
 * Configuration for the Medical Records System frontend
 */

const API_CONFIG = {
    // Backend API base URL
    BASE_URL: 'http://localhost:5000',
    
    // API endpoints
    ENDPOINTS: {
        AUTH: '/api/auth',
        USERS: '/api/users',
        PATIENTS: '/api/patients',
        RECORDS: '/api/records',
        ACCESS: '/api/access',
        ADMIN: '/api/admin'
    },
    
    // Helper to get full API URL
    getApiUrl: function(endpoint) {
        return `${this.BASE_URL}${endpoint}`;
    }
};

// Make it globally available
window.API_CONFIG = API_CONFIG;
