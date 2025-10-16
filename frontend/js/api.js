/**
 * API utilities for making authenticated requests to the backend
 */

class APIManager {
    constructor() {
        this.baseURL = window.API_CONFIG ? window.API_CONFIG.BASE_URL : 'http://localhost:5000';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generate unique request ID for tracking
     * @returns {string} Unique request ID
     */
    generateRequestId() {
        return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Get headers with authentication and request tracking
     * @returns {Object} Headers object
     */
    getHeaders() {
        return {
            ...this.defaultHeaders,
            ...window.authManager.getAuthHeader(),
            'X-Request-ID': this.generateRequestId()
        };
    }

    /**
     * Make authenticated API request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} API response
     */
    async request(endpoint, options = {}) {
        // Ensure endpoint starts with /api if not already
        const apiEndpoint = endpoint.startsWith('/api') ? endpoint : `/api${endpoint}`;
        const url = `${this.baseURL}${apiEndpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (response.ok) {
                return data;
            } else {
                // Handle token expiration
                if (response.status === 401 && window.authManager) {
                    const refreshed = await window.authManager.refreshToken();
                    if (refreshed) {
                        // Retry request with new token
                        config.headers = {
                            ...this.getHeaders(),
                            ...options.headers
                        };
                        const retryResponse = await fetch(url, config);
                        const retryData = await retryResponse.json();
                        
                        if (retryResponse.ok) {
                            return retryData;
                        } else {
                            throw new Error(retryData.error?.message || 'Request failed');
                        }
                    } else {
                        window.authManager.logout();
                        throw new Error(data.error?.message || 'Authentication failed');
                    }
                }
                
                throw new Error(data.error?.message || 'Request failed');
            }
        } catch (error) {
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query parameters
     * @returns {Promise<Object>} API response
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET'
        });
    }

    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise<Object>} API response
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body data
     * @returns {Promise<Object>} API response
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise<Object>} API response
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    /**
     * Upload file with encryption
     * @param {string} endpoint - Upload endpoint
     * @param {File} file - File to upload
     * @param {Object} metadata - Additional metadata
     * @returns {Promise<Object>} Upload response
     */
    async uploadFile(endpoint, file, metadata = {}) {
        try {
            // Encrypt file before upload
            const encryptionManager = new window.EncryptionManager();
            const encryptedFile = await encryptionManager.encryptFile(file);
            
            const uploadData = {
                encrypted_content: encryptedFile.encryptedContent,
                encryption_iv: encryptedFile.iv,
                file_size: encryptedFile.originalSize,
                mime_type: encryptedFile.mimeType,
                checksum: await encryptionManager.generateHash(encryptedFile.encryptedContent),
                ...metadata
            };

            return this.post(endpoint, uploadData);
        } catch (error) {
            return {
                success: false,
                error: {
                    code: 'ENCRYPTION_ERROR',
                    message: 'Failed to encrypt file for upload',
                    details: error.message
                }
            };
        }
    }

    // Medical Records API methods
    async uploadMedicalRecord(patientId, documentType, file, title, description = '') {
        return this.uploadFile('/records/upload', file, {
            patient_id: patientId,
            document_type: documentType,
            title: title,
            description: description
        });
    }

    async getMedicalRecord(documentId) {
        return this.get(`/records/${documentId}`);
    }

    async getPatientRecords(patientId, page = 1, limit = 10) {
        return this.get(`/records/patient/${patientId}`, { page, limit });
    }

    async deleteMedicalRecord(documentId) {
        return this.delete(`/records/${documentId}`);
    }

    // Access Control API methods
    async grantAccess(documentId, granteeId, accessLevel, expiresAt = null) {
        return this.post('/access/grant', {
            document_id: documentId,
            grantee_id: granteeId,
            access_level: accessLevel,
            expires_at: expiresAt
        });
    }

    async revokeAccess(grantId) {
        return this.delete(`/access/revoke/${grantId}`);
    }

    async getAccessGrants(documentId) {
        return this.get(`/access/grants/${documentId}`);
    }

    // User Management API methods
    async getUserProfile() {
        return this.get('/users/profile');
    }

    async updateUserProfile(profileData) {
        return this.put('/users/profile', profileData);
    }

    async searchUsers(query, role = null) {
        const params = { q: query };
        if (role) params.role = role;
        return this.get('/users/search', params);
    }

    // Admin API methods
    async getAllUsers(page = 1, limit = 20) {
        return this.get('/users', { page, limit });
    }

    async getUserById(userId) {
        return this.get(`/users/${userId}`);
    }

    async updateUserStatus(userId, isActive) {
        return this.put(`/users/${userId}/status`, { is_active: isActive });
    }

    async getAuditLogs(page = 1, limit = 50, filters = {}) {
        return this.get('/admin/audit-logs', { page, limit, ...filters });
    }
}

// Create global instance
window.apiManager = new APIManager();