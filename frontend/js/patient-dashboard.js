/**
 * Patient Dashboard JavaScript
 * Handles patient-specific functionality and UI interactions
 */

class PatientDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.currentPage = 1;
        this.recordsPerPage = 10;
        this.patientId = null;
        this.init();
    }

    async init() {
        // Check authentication and role
        if (!window.authManager.isAuthenticated() || !window.authManager.hasRole('patient')) {
            window.location.href = 'login.html';
            return;
        }

        // Get patient ID from user data
        const userData = window.authManager.getUserData();
        this.patientId = userData.id;

        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadDashboardData();
        await this.loadUserProfile();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                if (section) {
                    this.showSection(section);
                }
            });
        });

        // Upload form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleDocumentUpload(e));
        }

        // Profile form
        const profileForm = document.getElementById('profileForm');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => this.handleProfileUpdate(e));
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('page-btn')) {
                const page = parseInt(e.target.dataset.page);
                this.loadRecords(page);
            }
        });
    }

    async loadDashboardData() {
        try {
            this.showLoading(true);
            
            // Load recent records
            const recentRecords = await window.apiManager.get(`/records/patient/${this.patientId}`, { limit: 5 });
            this.displayRecentRecords(recentRecords.records || []);
            
            // Load statistics (mock data for now)
            const stats = {
                total_records: recentRecords.records ? recentRecords.records.length : 0,
                recent_uploads: 0,
                shared_records: 0
            };
            this.displayStats(stats);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            window.uiManager.showError('Failed to load dashboard data');
        } finally {
            this.showLoading(false);
        }
    }

    async loadUserProfile() {
        try {
            const response = await window.apiManager.get(`/users/profile`);
            this.displayUserProfile(response.profile);
        } catch (error) {
            console.error('Error loading user profile:', error);
            window.uiManager.showError('Failed to load user profile');
        }
    }

    async loadRecords(page = 1) {
        try {
            this.showLoading(true);
            this.currentPage = page;
            
            const offset = (page - 1) * this.recordsPerPage;
            const response = await window.apiManager.get(`/records/patient/${this.patientId}`, {
                limit: this.recordsPerPage,
                page: page
            });
            
            this.displayRecords(response.records || []);
            this.displayPagination(response.pagination?.total || 0, page);
            
        } catch (error) {
            console.error('Error loading records:', error);
            window.uiManager.showError('Failed to load medical records');
        } finally {
            this.showLoading(false);
        }
    }

    displayRecentRecords(records) {
        const container = document.getElementById('recentRecords');
        if (!container) return;

        if (!records || records.length === 0) {
            container.innerHTML = '<p class="no-data">No recent records found</p>';
            return;
        }

        container.innerHTML = records.map(record => `
            <div class="record-card">
                <div class="record-header">
                    <h4>${record.title || record.document_type}</h4>
                    <span class="record-date">${new Date(record.created_at).toLocaleDateString()}</span>
                </div>
                <p class="record-description">${record.description || 'No description available'}</p>
                <div class="record-meta">
                    <span class="record-type">${record.document_type}</span>
                    <span class="record-doctor">Dr. ${record.doctor_name}</span>
                </div>
            </div>
        `).join('');
    }

    displayStats(stats) {
        const elements = {
            totalRecords: document.getElementById('totalRecords'),
            recentUploads: document.getElementById('recentUploads'),
            sharedRecords: document.getElementById('sharedRecords')
        };

        if (elements.totalRecords) elements.totalRecords.textContent = stats.total_records || 0;
        if (elements.recentUploads) elements.recentUploads.textContent = stats.recent_uploads || 0;
        if (elements.sharedRecords) elements.sharedRecords.textContent = stats.shared_records || 0;
    }

    displayUserProfile(profile) {
        const elements = {
            userName: document.getElementById('userName'),
            userEmail: document.getElementById('userEmail'),
            profileFirstName: document.getElementById('profileFirstName'),
            profileLastName: document.getElementById('profileLastName'),
            profileEmail: document.getElementById('profileEmail'),
            profilePhone: document.getElementById('profilePhone'),
            profileDob: document.getElementById('profileDob')
        };

        if (elements.userName) elements.userName.textContent = `${profile.first_name} ${profile.last_name}`;
        if (elements.userEmail) elements.userEmail.textContent = profile.email;
        if (elements.profileFirstName) elements.profileFirstName.value = profile.first_name || '';
        if (elements.profileLastName) elements.profileLastName.value = profile.last_name || '';
        if (elements.profileEmail) elements.profileEmail.value = profile.email || '';
        if (elements.profilePhone) elements.profilePhone.value = profile.profile?.phone || '';
        if (elements.profileDob) elements.profileDob.value = profile.date_of_birth || '';
    }

    displayRecords(records) {
        const container = document.getElementById('recordsList');
        if (!container) return;

        if (!records || records.length === 0) {
            container.innerHTML = '<p class="no-data">No medical records found</p>';
            return;
        }

        container.innerHTML = records.map(record => `
            <div class="record-item">
                <div class="record-info">
                    <h4>${record.title || record.document_type}</h4>
                    <p>${record.description || 'No description available'}</p>
                    <div class="record-meta">
                        <span class="record-type">${record.document_type}</span>
                        <span class="record-date">${new Date(record.created_at).toLocaleDateString()}</span>
                        <span class="record-doctor">Dr. ${record.doctor_name}</span>
                    </div>
                </div>
                <div class="record-actions">
                    <button class="btn btn-primary" onclick="patientDashboard.viewRecord('${record._id}')">
                        View
                    </button>
                    <button class="btn btn-secondary" onclick="patientDashboard.downloadRecord('${record._id}')">
                        Download
                    </button>
                </div>
            </div>
        `).join('');
    }

    displayPagination(total, currentPage) {
        const container = document.getElementById('pagination');
        if (!container) return;

        const totalPages = Math.ceil(total / this.recordsPerPage);
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHTML = '';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `<button class="page-btn" data-page="${currentPage - 1}">Previous</button>`;
        }

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === currentPage) {
                paginationHTML += `<button class="page-btn active" data-page="${i}">${i}</button>`;
            } else if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                paginationHTML += `<button class="page-btn" data-page="${i}">${i}</button>`;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                paginationHTML += `<span class="page-ellipsis">...</span>`;
            }
        }

        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `<button class="page-btn" data-page="${currentPage + 1}">Next</button>`;
        }

        container.innerHTML = paginationHTML;
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.dashboard-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}Section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        this.currentSection = sectionName;

        // Load section-specific data
        if (sectionName === 'records') {
            this.loadRecords();
        }
    }

    async handleDocumentUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const file = formData.get('document');
        
        if (!file) {
            window.uiManager.showError('Please select a file to upload');
            return;
        }

        try {
            this.showLoading(true);
            
            // Encrypt file content
            const fileContent = await this.readFileAsText(file);
            const encryptedContent = await window.encryptionManager.encrypt(fileContent);
            
            // Prepare upload data
            const uploadData = {
                title: formData.get('title'),
                description: formData.get('description'),
                document_type: formData.get('document_type'),
                encrypted_content: encryptedContent.data,
                encryption_key_id: encryptedContent.keyId,
                file_size: file.size,
                mime_type: file.type,
                checksum: await window.encryptionManager.calculateChecksum(fileContent)
            };

            await window.apiClient.post('/records', uploadData);
            
            window.uiManager.showSuccess('Document uploaded successfully');
            event.target.reset();
            
            // Refresh records if on records section
            if (this.currentSection === 'records') {
                this.loadRecords();
            }
            
        } catch (error) {
            console.error('Error uploading document:', error);
            window.uiManager.showError('Failed to upload document');
        } finally {
            this.showLoading(false);
        }
    }

    async handleProfileUpdate(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const profileData = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            profile: {
                phone: formData.get('phone')
            }
        };

        try {
            this.showLoading(true);
            
            await window.apiClient.put('/users/profile', profileData);
            
            window.uiManager.showSuccess('Profile updated successfully');
            this.loadUserProfile();
            
        } catch (error) {
            console.error('Error updating profile:', error);
            window.uiManager.showError('Failed to update profile');
        } finally {
            this.showLoading(false);
        }
    }

    async handleSearch(query) {
        if (!query.trim()) {
            this.loadRecords();
            return;
        }

        try {
            const results = await window.apiClient.get(
                `/records/patient/${this.patientId}/search?q=${encodeURIComponent(query)}`
            );
            this.displayRecords(results.data);
        } catch (error) {
            console.error('Error searching records:', error);
            window.uiManager.showError('Search failed');
        }
    }

    async viewRecord(recordId) {
        try {
            this.showLoading(true);
            
            const record = await window.apiClient.get(`/records/${recordId}`);
            
            // Decrypt content
            const decryptedContent = await window.encryptionManager.decrypt(
                record.encrypted_content,
                record.encryption_key_id
            );
            
            // Show in modal or new page
            this.showRecordModal(record, decryptedContent);
            
        } catch (error) {
            console.error('Error viewing record:', error);
            window.uiManager.showError('Failed to load record');
        } finally {
            this.showLoading(false);
        }
    }

    async downloadRecord(recordId) {
        try {
            this.showLoading(true);
            
            const record = await window.apiClient.get(`/records/${recordId}`);
            
            // Decrypt content
            const decryptedContent = await window.encryptionManager.decrypt(
                record.encrypted_content,
                record.encryption_key_id
            );
            
            // Create download
            const blob = new Blob([decryptedContent], { type: record.mime_type });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = record.title || `record_${recordId}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error downloading record:', error);
            window.uiManager.showError('Failed to download record');
        } finally {
            this.showLoading(false);
        }
    }

    showRecordModal(record, content) {
        // Implementation for showing record in modal
        // This would create a modal dialog to display the record content
        console.log('Showing record:', record.title, content);
    }

    handleLogout() {
        window.authManager.logout();
        // The authManager.logout() will handle the redirect
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    showLoading(show) {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.patientDashboard = new PatientDashboard();
});