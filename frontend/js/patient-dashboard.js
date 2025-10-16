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
        console.log('Patient dashboard initializing...');
        
        // Check authentication and role
        if (!window.authManager || !window.authManager.isAuthenticated()) {
            console.log('Not authenticated, redirecting to login');
            window.location.href = 'login.html';
            return;
        }

        if (!window.authManager.hasRole('patient')) {
            console.log('Not a patient, redirecting');
            window.location.href = '../index.html';
            return;
        }

        // Get patient ID from user data
        const userData = window.authManager.getUserData();
        this.patientId = userData.id || userData._id;
        console.log('Patient ID:', this.patientId);

        // Setup event listeners
        this.setupEventListeners();
        console.log('Event listeners set up');
        
        // Load initial data
        try {
            await this.loadDashboardData();
            await this.loadUserProfile();
            console.log('Dashboard data loaded');
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
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
        document.querySelectorAll('.logout-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        });

        // Search functionality
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Doctor search for access control
        const searchDoctor = document.getElementById('searchDoctor');
        if (searchDoctor) {
            searchDoctor.addEventListener('input', (e) => this.searchDoctors(e.target.value));
        }

        // Grant access form
        const grantAccessForm = document.getElementById('grantAccessForm');
        if (grantAccessForm) {
            grantAccessForm.addEventListener('submit', (e) => this.handleGrantAccess(e));
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
            
            // Update statistics
            const totalRecordsEl = document.getElementById('totalRecords');
            if (totalRecordsEl) {
                totalRecordsEl.textContent = recentRecords.pagination?.total || recentRecords.records?.length || 0;
            }
            
            // Load access grants count
            try {
                // This would need a dedicated endpoint - for now using placeholder
                const activeGrantsEl = document.getElementById('activeGrants');
                if (activeGrantsEl) {
                    activeGrantsEl.textContent = '0';
                }
            } catch (e) {
                console.log('Could not load access grants');
            }
            
            // Set last activity
            const lastActivityEl = document.getElementById('lastActivity');
            if (lastActivityEl && recentRecords.records && recentRecords.records.length > 0) {
                const lastRecord = recentRecords.records[0];
                const lastDate = new Date(lastRecord.created_at);
                lastActivityEl.textContent = lastDate.toLocaleDateString();
            }
            
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
        console.log('Showing section:', sectionName);
        
        // Hide all sections
        const allSections = document.querySelectorAll('.content-section');
        console.log('Found sections:', allSections.length);
        allSections.forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionName);
        console.log('Target section:', targetSection);
        if (targetSection) {
            targetSection.classList.add('active');
            console.log('Section activated:', sectionName);
        } else {
            console.error('Section not found:', sectionName);
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
        } else if (sectionName === 'access') {
            this.loadAccessControl();
        } else if (sectionName === 'profile') {
            this.loadUserProfile();
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

    async loadAccessControl() {
        try {
            // Load documents for access control dropdown
            const records = await window.apiManager.get(`/records/patient/${this.patientId}`);
            const selectDocument = document.getElementById('selectDocument');
            
            if (selectDocument && records.records) {
                selectDocument.innerHTML = '<option value="">Choose a document</option>' +
                    records.records.map(record => 
                        `<option value="${record._id || record.id}">${record.title || record.document_type}</option>`
                    ).join('');
            }
            
            // Load active access grants
            await this.loadActiveAccessGrants();
            
        } catch (error) {
            console.error('Error loading access control:', error);
            window.uiManager.showError('Failed to load access control data');
        }
    }

    async loadActiveAccessGrants() {
        try {
            // This would need a dedicated endpoint to list all grants for a patient
            const activeAccessList = document.getElementById('activeAccessList');
            if (activeAccessList) {
                activeAccessList.innerHTML = '<p class="no-data">No active access grants</p>';
            }
        } catch (error) {
            console.error('Error loading access grants:', error);
        }
    }

    async handleGrantAccess(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const grantData = {
            document_id: formData.get('document_id'),
            grantee_id: formData.get('grantee_id'),
            access_level: formData.get('access_level'),
            expires_at: formData.get('expires_at') || null,
            reason: formData.get('reason')
        };

        try {
            this.showLoading(true);
            
            await window.apiManager.post('/access/grant', grantData);
            
            window.uiManager.showSuccess('Access granted successfully');
            event.target.reset();
            await this.loadActiveAccessGrants();
            
        } catch (error) {
            console.error('Error granting access:', error);
            window.uiManager.showError('Failed to grant access');
        } finally {
            this.showLoading(false);
        }
    }

    async searchDoctors(query) {
        if (!query || query.length < 2) {
            document.getElementById('doctorResults').innerHTML = '';
            return;
        }

        try {
            const results = await window.apiManager.get('/users/search', { 
                q: query, 
                role: 'doctor' 
            });
            
            const resultsContainer = document.getElementById('doctorResults');
            if (resultsContainer) {
                if (results.users && results.users.length > 0) {
                    resultsContainer.innerHTML = results.users.map(doctor => `
                        <div class="search-result-item" onclick="patientDashboard.selectDoctor('${doctor.id}', '${doctor.first_name} ${doctor.last_name}')">
                            <strong>${doctor.first_name} ${doctor.last_name}</strong>
                            <small>${doctor.specialization || 'Doctor'}</small>
                        </div>
                    `).join('');
                } else {
                    resultsContainer.innerHTML = '<p class="no-data">No doctors found</p>';
                }
            }
        } catch (error) {
            console.error('Error searching doctors:', error);
        }
    }

    selectDoctor(doctorId, doctorName) {
        const searchInput = document.getElementById('searchDoctor');
        if (searchInput) {
            searchInput.value = doctorName;
            searchInput.setAttribute('data-doctor-id', doctorId);
        }
        document.getElementById('doctorResults').innerHTML = '';
    }

    showLoading(show) {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
}

// Make showSection globally accessible
window.showSection = function(sectionName) {
    console.log('Global showSection called:', sectionName);
    if (window.patientDashboard) {
        window.patientDashboard.showSection(sectionName);
    } else {
        console.error('Patient dashboard not initialized');
    }
};

// Simple direct navigation function as backup
window.switchSection = function(sectionName) {
    console.log('Direct switch to:', sectionName);
    
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const target = document.getElementById(sectionName);
    if (target) {
        target.classList.add('active');
        console.log('Section shown:', sectionName);
    } else {
        console.error('Section not found:', sectionName);
    }
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing patient dashboard');
    window.patientDashboard = new PatientDashboard();
});