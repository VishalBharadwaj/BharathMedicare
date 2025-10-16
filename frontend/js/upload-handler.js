// Simple upload handler for patient dashboard
document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    if (!uploadForm) return;
    
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('documentFile');
        const file = fileInput ? fileInput.files[0] : null;
        
        if (!file) {
            alert('Please select a file to upload');
            return;
        }
        
        if (file.size > 16 * 1024 * 1024) {
            alert('File size must be less than 16MB');
            return;
        }
        
        const submitBtn = uploadForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '🔄 Uploading...';
        
        try {
            const userData = window.authManager.getUserData();
            const patientId = userData.id || userData._id;
            
            // Read file as base64
            const reader = new FileReader();
            const fileContent = await new Promise((resolve, reject) => {
                reader.onload = () => resolve(reader.result.split(',')[1]);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
            
            const uploadData = {
                patient_id: patientId,
                title: document.getElementById('documentTitle').value,
                description: document.getElementById('documentDescription').value,
                document_type: document.getElementById('documentType').value,
                file_content: fileContent,
                file_name: file.name,
                file_size: file.size,
                mime_type: file.type
            };
            
            console.log('Uploading document:', uploadData.title, uploadData.file_name);
            
            const response = await window.apiManager.post('/records/upload', uploadData);
            
            console.log('Upload response:', response);
            alert('Document uploaded successfully!');
            uploadForm.reset();
            
            // Switch to records section if showSection function exists
            if (typeof showSection === 'function') {
                showSection('records');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload document: ' + error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
});
