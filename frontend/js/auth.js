/**
 * Authentication utilities for JWT token management and user session handling
 */

class AuthManager {
    constructor() {
        this.tokenKey = 'medical_access_token';
        this.refreshTokenKey = 'medical_refresh_token';
        this.userKey = 'medical_user_data';
        this.baseURL = 'http://localhost:5000/api/auth';
    }

    /**
     * Store authentication tokens securely
     * @param {string} accessToken - JWT access token
     * @param {string} refreshToken - JWT refresh token
     * @param {Object} userData - User information
     */
    storeTokens(accessToken, refreshToken, userData) {
        // Use sessionStorage for access token (more secure)
        sessionStorage.setItem(this.tokenKey, accessToken);
        
        // Use localStorage for refresh token (persistent across sessions)
        localStorage.setItem(this.refreshTokenKey, refreshToken);
        localStorage.setItem(this.userKey, JSON.stringify(userData));
    }

    /**
     * Get stored access token
     * @returns {string|null} Access token or null if not found
     */
    getAccessToken() {
        return sessionStorage.getItem(this.tokenKey);
    }

    /**
     * Get stored refresh token
     * @returns {string|null} Refresh token or null if not found
     */
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    /**
     * Get stored user data
     * @returns {Object|null} User data or null if not found
     */
    getUserData() {
        const userData = localStorage.getItem(this.userKey);
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Clear all stored authentication data
     */
    clearTokens() {
        sessionStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userKey);
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} True if authenticated
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Get authorization header for API requests
     * @returns {Object} Authorization header object
     */
    getAuthHeader() {
        const token = this.getAccessToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    /**
     * Login user with email and password
     * @param {string} email - User email
     * @param {string} password - User password
     * @param {string} mfaToken - Optional MFA token
     * @returns {Promise<Object>} Login response
     */
    async login(email, password, mfaToken = null) {
        try {
            const response = await fetch(`${this.baseURL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    mfa_token: mfaToken
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.storeTokens(data.access_token, data.refresh_token, data.user);
                return { success: true, data };
            } else {
                return { success: false, error: data.error };
            }
        } catch (error) {
            return { 
                success: false, 
                error: { 
                    code: 'NETWORK_ERROR', 
                    message: 'Network error occurred during login' 
                } 
            };
        }
    }

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Promise<Object>} Registration response
     */
    async register(userData) {
        try {
            const response = await fetch(`${this.baseURL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            return response.ok ? { success: true, data } : { success: false, error: data.error };
        } catch (error) {
            return { 
                success: false, 
                error: { 
                    code: 'NETWORK_ERROR', 
                    message: 'Network error occurred during registration' 
                } 
            };
        }
    }

    /**
     * Refresh access token using refresh token
     * @returns {Promise<boolean>} True if refresh successful
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                sessionStorage.setItem(this.tokenKey, data.access_token);
                return true;
            } else {
                // Refresh token is invalid, clear all tokens
                this.clearTokens();
                return false;
            }
        } catch (error) {
            this.clearTokens();
            return false;
        }
    }

    /**
     * Validate current access token
     * @returns {Promise<boolean>} True if token is valid
     */
    async validateToken() {
        const token = this.getAccessToken();
        if (!token) return false;

        try {
            const response = await fetch(`${this.baseURL}/validate`, {
                method: 'GET',
                headers: this.getAuthHeader()
            });

            if (response.ok) {
                return true;
            } else if (response.status === 401) {
                // Try to refresh token
                return await this.refreshToken();
            } else {
                return false;
            }
        } catch (error) {
            return false;
        }
    }

    /**
     * Logout user and clear all tokens
     */
    logout() {
        this.clearTokens();
        window.location.href = 'pages/login.html';
    }

    /**
     * Check user role
     * @param {string} requiredRole - Required role to check
     * @returns {boolean} True if user has required role
     */
    hasRole(requiredRole) {
        const userData = this.getUserData();
        return userData && userData.role === requiredRole;
    }

    /**
     * Get user's full name
     * @returns {string} User's full name
     */
    getUserFullName() {
        const userData = this.getUserData();
        return userData ? `${userData.first_name} ${userData.last_name}` : '';
    }

    /**
     * Initialize authentication check on page load
     */
    async init() {
        // Check if we're on a public page
        const publicPages = ['/pages/login.html', '/pages/register.html', '/index.html', '/'];
        const currentPage = window.location.pathname;
        
        if (publicPages.includes(currentPage)) {
            return;
        }

        // Validate token for protected pages
        const isValid = await this.validateToken();
        if (!isValid) {
            this.logout();
        }
    }
}

// Create global instance
window.authManager = new AuthManager();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.authManager.init();
});