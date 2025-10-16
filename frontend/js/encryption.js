/**
 * Client-side AES-256 encryption utilities for medical records
 * Implements HIPAA-compliant encryption before data transmission
 */

class EncryptionManager {
    constructor() {
        this.algorithm = 'AES-GCM';
        this.keyLength = 256;
    }

    /**
     * Generate a new AES-256 encryption key
     * @returns {Promise<CryptoKey>} Generated encryption key
     */
    async generateKey() {
        return await window.crypto.subtle.generateKey(
            {
                name: this.algorithm,
                length: this.keyLength
            },
            true, // extractable
            ['encrypt', 'decrypt']
        );
    }

    /**
     * Export key to raw format for storage
     * @param {CryptoKey} key - The key to export
     * @returns {Promise<ArrayBuffer>} Raw key data
     */
    async exportKey(key) {
        return await window.crypto.subtle.exportKey('raw', key);
    }

    /**
     * Import key from raw format
     * @param {ArrayBuffer} keyData - Raw key data
     * @returns {Promise<CryptoKey>} Imported key
     */
    async importKey(keyData) {
        return await window.crypto.subtle.importKey(
            'raw',
            keyData,
            { name: this.algorithm },
            true,
            ['encrypt', 'decrypt']
        );
    }

    /**
     * Encrypt data using AES-256-GCM
     * @param {string} plaintext - Data to encrypt
     * @param {CryptoKey} key - Encryption key
     * @returns {Promise<Object>} Encrypted data with IV
     */
    async encryptData(plaintext, key) {
        const encoder = new TextEncoder();
        const data = encoder.encode(plaintext);
        
        // Generate random IV
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: this.algorithm,
                iv: iv
            },
            key,
            data
        );

        return {
            encrypted: new Uint8Array(encrypted),
            iv: iv
        };
    }

    /**
     * Decrypt data using AES-256-GCM
     * @param {Uint8Array} encryptedData - Encrypted data
     * @param {Uint8Array} iv - Initialization vector
     * @param {CryptoKey} key - Decryption key
     * @returns {Promise<string>} Decrypted plaintext
     */
    async decryptData(encryptedData, iv, key) {
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: this.algorithm,
                iv: iv
            },
            key,
            encryptedData
        );

        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    }

    /**
     * Convert ArrayBuffer to Base64 string
     * @param {ArrayBuffer} buffer - Buffer to convert
     * @returns {string} Base64 encoded string
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    /**
     * Convert Base64 string to ArrayBuffer
     * @param {string} base64 - Base64 encoded string
     * @returns {ArrayBuffer} Decoded buffer
     */
    base64ToArrayBuffer(base64) {
        const binary = window.atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }

    /**
     * Encrypt file content for upload
     * @param {File} file - File to encrypt
     * @returns {Promise<Object>} Encrypted file data
     */
    async encryptFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = async (event) => {
                try {
                    const fileContent = event.target.result;
                    const key = await this.generateKey();
                    const keyData = await this.exportKey(key);
                    
                    // Convert file content to base64 for encryption
                    const base64Content = this.arrayBufferToBase64(fileContent);
                    
                    // Encrypt the content
                    const encrypted = await this.encryptData(base64Content, key);
                    
                    resolve({
                        encryptedContent: this.arrayBufferToBase64(encrypted.encrypted),
                        iv: this.arrayBufferToBase64(encrypted.iv),
                        key: this.arrayBufferToBase64(keyData),
                        originalSize: file.size,
                        mimeType: file.type,
                        fileName: file.name
                    });
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * Decrypt file content for download
     * @param {string} encryptedContent - Base64 encrypted content
     * @param {string} iv - Base64 initialization vector
     * @param {string} keyData - Base64 encryption key
     * @returns {Promise<Blob>} Decrypted file blob
     */
    async decryptFile(encryptedContent, iv, keyData, mimeType) {
        try {
            // Convert base64 to ArrayBuffers
            const encrypted = new Uint8Array(this.base64ToArrayBuffer(encryptedContent));
            const ivBuffer = new Uint8Array(this.base64ToArrayBuffer(iv));
            const keyBuffer = this.base64ToArrayBuffer(keyData);
            
            // Import the key
            const key = await this.importKey(keyBuffer);
            
            // Decrypt the content
            const decryptedBase64 = await this.decryptData(encrypted, ivBuffer, key);
            
            // Convert back to binary data
            const binaryData = this.base64ToArrayBuffer(decryptedBase64);
            
            return new Blob([binaryData], { type: mimeType });
        } catch (error) {
            throw new Error('Failed to decrypt file: ' + error.message);
        }
    }

    /**
     * Generate secure hash of data for integrity checking
     * @param {string} data - Data to hash
     * @returns {Promise<string>} SHA-256 hash as hex string
     */
    async generateHash(data) {
        const encoder = new TextEncoder();
        const dataBuffer = encoder.encode(data);
        const hashBuffer = await window.crypto.subtle.digest('SHA-256', dataBuffer);
        const hashArray = new Uint8Array(hashBuffer);
        return Array.from(hashArray).map(b => b.toString(16).padStart(2, '0')).join('');
    }
}

// Export for use in other modules
window.EncryptionManager = EncryptionManager;