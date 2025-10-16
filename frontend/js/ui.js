/**
 * UI utilities for common interface operations and user feedback
 */

class UIManager {
    constructor() {
        this.loadingElements = new Set();
        this.notifications = [];
    }

    /**
     * Show loading spinner on element
     * @param {string|HTMLElement} element - Element selector or element
     * @param {string} text - Loading text
     */
    showLoading(element, text = 'Loading...') {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;

        el.disabled = true;
        el.classList.add('loading');
        
        const originalText = el.textContent;
        el.setAttribute('data-original-text', originalText);
        el.textContent = text;
        
        this.loadingElements.add(el);
    }

    /**
     * Hide loading spinner from element
     * @param {string|HTMLElement} element - Element selector or element
     */
    hideLoading(element) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) return;

        el.disabled = false;
        el.classList.remove('loading');
        
        const originalText = el.getAttribute('data-original-text');
        if (originalText) {
            el.textContent = originalText;
            el.removeAttribute('data-original-text');
        }
        
        this.loadingElements.delete(el);
    }

    /**
     * Show notification message
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
     */
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Add to notifications container or create one
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }

        container.appendChild(notification);
        this.notifications.push(notification);

        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                    this.notifications = this.notifications.filter(n => n !== notification);
                }
            }, duration);
        }

        return notification;
    }

    /**
     * Show success notification
     * @param {string} message - Success message
     */
    showSuccess(message) {
        return this.showNotification(message, 'success');
    }

    /**
     * Show error notification
     * @param {string} message - Error message
     */
    showError(message) {
        return this.showNotification(message, 'error', 0); // Don't auto-hide errors
    }

    /**
     * Show warning notification
     * @param {string} message - Warning message
     */
    showWarning(message) {
        return this.showNotification(message, 'warning');
    }

    /**
     * Clear all notifications
     */
    clearNotifications() {
        this.notifications.forEach(notification => {
            if (notification.parentElement) {
                notification.remove();
            }
        });
        this.notifications = [];
    }

    /**
     * Show confirmation dialog
     * @param {string} message - Confirmation message
     * @param {string} title - Dialog title
     * @returns {Promise<boolean>} True if confirmed
     */
    async showConfirmation(message, title = 'Confirm Action') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal modal-confirmation';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="this.closest('.modal').remove(); window.confirmationResolve(false);">Cancel</button>
                        <button class="btn btn-primary" onclick="this.closest('.modal').remove(); window.confirmationResolve(true);">Confirm</button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            
            // Store resolve function globally for button handlers
            window.confirmationResolve = resolve;
            
            // Close on backdrop click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(false);
                }
            });
        });
    }

    /**
     * Format file size for display
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Format date for display
     * @param {string|Date} date - Date to format
     * @returns {string} Formatted date
     */
    formatDate(date) {
        const d = new Date(date);
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
    }

    /**
     * Validate form fields
     * @param {HTMLFormElement} form - Form to validate
     * @returns {Object} Validation result
     */
    validateForm(form) {
        const errors = [];
        const formData = new FormData(form);
        const data = {};

        // Convert FormData to object
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        // Check required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                errors.push(`${field.name || field.id} is required`);
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });

        // Email validation
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                errors.push('Please enter a valid email address');
                field.classList.add('error');
            }
        });

        // Password validation
        const passwordFields = form.querySelectorAll('input[type="password"]');
        passwordFields.forEach(field => {
            if (field.value && field.value.length < 8) {
                errors.push('Password must be at least 8 characters long');
                field.classList.add('error');
            }
        });

        return {
            isValid: errors.length === 0,
            errors: errors,
            data: data
        };
    }

    /**
     * Validate email format
     * @param {string} email - Email to validate
     * @returns {boolean} True if valid email
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Populate user navigation
     */
    populateUserNav() {
        const userData = window.authManager.getUserData();
        if (!userData) return;

        const userNameElements = document.querySelectorAll('.user-name');
        const userRoleElements = document.querySelectorAll('.user-role');
        
        userNameElements.forEach(el => {
            el.textContent = `${userData.first_name} ${userData.last_name}`;
        });
        
        userRoleElements.forEach(el => {
            el.textContent = userData.role.charAt(0).toUpperCase() + userData.role.slice(1);
        });
    }

    /**
     * Setup logout functionality
     */
    setupLogout() {
        const logoutButtons = document.querySelectorAll('.logout-btn');
        logoutButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                window.authManager.logout();
            });
        });
    }

    /**
     * Initialize common UI components
     */
    init() {
        this.populateUserNav();
        this.setupLogout();
        
        // Setup form validation
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('validate')) {
                e.preventDefault();
                const validation = this.validateForm(form);
                
                if (!validation.isValid) {
                    this.showError(validation.errors.join('<br>'));
                    return false;
                }
                
                // If validation passes, allow form submission
                return true;
            }
        });

        // Setup file input styling
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                const label = document.querySelector(`label[for="${input.id}"]`);
                if (label && file) {
                    label.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
                }
            });
        });
    }
}

// Create global instance
window.uiManager = new UIManager();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.uiManager.init();
});