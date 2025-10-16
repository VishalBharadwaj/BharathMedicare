// Load and display patient records
document.addEventListener('DOMContentLoaded', () => {
    // Load records when page loads or when switching to records section
    loadPatientRecords();
    
    // Also reload when switching to records section
    const recordsLink = document.querySelector('[onclick*="records"]');
    if (recordsLink) {
        recordsLink.addEventListener('click', () => {
            setTimeout(loadPatientRecords, 100);
        });
    }
});

async function loadPatientRecords() {
    const recordsList = document.getElementById('recordsList');
    if (!recordsList) return;
    
    // Check if we're on the records section
    const recordsSection = document.getElementById('records');
    if (!recordsSection || !recordsSection.classList.contains('active')) {
        return;
    }
    
    try {
        recordsList.innerHTML = '<div class="loading-placeholder">Loading your medical records...</div>';
        
        const userData = window.authManager.getUserData();
        const patientId = userData.id || userData._id;
        
        console.log('Loading records for patient:', patientId);
        
        const response = await window.apiManager.get(`/records/patient/${patientId}`, {
            page: 1,
            limit: 50
        });
        
        console.log('Records response:', response);
        
        if (response.records && response.records.length > 0) {
            displayRecords(response.records);
        } else {
            recordsList.innerHTML = `
                <div class="empty-state">
                    <h4>No Medical Records Found</h4>
                    <p>You haven't uploaded any medical records yet.</p>
                    <button class="btn btn-primary" onclick="showSection('upload')">
                        📤 Upload Your First Document
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading records:', error);
        recordsList.innerHTML = `
            <div class="empty-state">
                <h4>Failed to Load Records</h4>
                <p>Error: ${error.message}</p>
                <button class="btn btn-secondary" onclick="loadPatientRecords()">
                    🔄 Try Again
                </button>
            </div>
        `;
    }
}

function displayRecords(records) {
    const recordsList = document.getElementById('recordsList');
    
    const html = records.map(record => `
        <div class="record-item">
            <div class="record-info">
                <h4>${record.title || record.document_type}</h4>
                <p>${record.description || 'No description available'}</p>
                <div class="record-meta">
                    <span class="record-type">${formatDocumentType(record.document_type)}</span>
                    <span class="record-date">${formatDate(record.created_at)}</span>
                    <span class="record-size">${formatFileSize(record.file_size)}</span>
                </div>
            </div>
            <div class="record-actions">
                <button class="btn btn-primary btn-sm" onclick="viewRecord('${record.id}')">
                    👁️ View
                </button>
                <button class="btn btn-secondary btn-sm" onclick="downloadRecord('${record.id}', '${record.title}')">
                    📥 Download
                </button>
            </div>
        </div>
    `).join('');
    
    recordsList.innerHTML = html;
}

function formatDocumentType(type) {
    const types = {
        'lab_result': 'Lab Results',
        'prescription': 'Prescription',
        'diagnosis': 'Diagnosis',
        'imaging': 'Medical Imaging',
        'consultation': 'Consultation Notes'
    };
    return types[type] || type;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function viewRecord(recordId) {
    try {
        const response = await window.apiManager.get(`/records/${recordId}`);
        const record = response.document;
        
        // Create a modal or alert to show record details
        const details = `
Title: ${record.title}
Type: ${formatDocumentType(record.document_type)}
Description: ${record.description || 'N/A'}
Date: ${formatDate(record.created_at)}
Size: ${formatFileSize(record.file_size)}
        `;
        
        alert(details);
    } catch (error) {
        console.error('Error viewing record:', error);
        alert('Failed to load record details: ' + error.message);
    }
}

async function downloadRecord(recordId, title) {
    try {
        const response = await window.apiManager.get(`/records/${recordId}`);
        const record = response.document;
        
        // Decode base64 content
        const byteCharacters = atob(record.encrypted_content);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: record.mime_type });
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = record.file_name || title || 'document';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert('Download started!');
    } catch (error) {
        console.error('Error downloading record:', error);
        alert('Failed to download record: ' + error.message);
    }
}

// Make functions globally available
window.loadPatientRecords = loadPatientRecords;
window.viewRecord = viewRecord;
window.downloadRecord = downloadRecord;
