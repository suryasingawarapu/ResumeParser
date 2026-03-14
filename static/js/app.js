/**
 * Frontend JavaScript for Resume Processing System
 * Handles form submissions, loading states, error display, and results rendering
 */

document.addEventListener('DOMContentLoaded', function() {
    const zipForm = document.getElementById('zipForm');
    const driveForm = document.getElementById('driveForm');
    const singleForm = document.getElementById('singleForm');
    const clearBtn = document.getElementById('clearBtn');
    
    if (zipForm) {
        zipForm.addEventListener('submit', handleZipUpload);
    }
    
    if (driveForm) {
        driveForm.addEventListener('submit', handleDriveUpload);
    }
    
    if (singleForm) {
        singleForm.addEventListener('submit', handleSingleUpload);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearResults);
    }
});

/**
 * Handle ZIP file upload
 * @param {Event} e - Form submission event
 */
async function handleZipUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('zipFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a ZIP file');
        return;
    }
    
    if (!file.name.toLowerCase().endsWith('.zip')) {
        showError('Please select a valid ZIP file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    await submitForm('/upload-zip', formData);
    fileInput.value = '';
}

/**
 * Handle Google Drive folder link submission
 * @param {Event} e - Form submission event
 */
async function handleDriveUpload(e) {
    e.preventDefault();
    
    const linkInput = document.getElementById('driveLink');
    const link = linkInput.value.trim();
    
    if (!link) {
        showError('Please enter a Google Drive folder link');
        return;
    }
    
    if (!link.includes('drive.google.com')) {
        showError('Please enter a valid Google Drive link');
        return;
    }
    
    const formData = new FormData();
    formData.append('folder_link', link);
    
    await submitForm('/upload-drive', formData);
    linkInput.value = '';
}

/**
 * Handle single resume file upload
 * @param {Event} e - Form submission event
 */
async function handleSingleUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('singleFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a resume file');
        return;
    }
    
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.pdf') && !fileName.endsWith('.docx')) {
        showError('Please select a PDF or DOCX file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    await submitForm('/upload-single', formData);
    fileInput.value = '';
}

/**
 * Submit form data to server
 * @param {string} endpoint - API endpoint URL
 * @param {FormData} formData - Form data to submit
 */
async function submitForm(endpoint, formData) {
    showLoading(true);
    clearError();
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData,
            timeout: 60000
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showError(data.error || 'An error occurred during processing');
            return;
        }
        
        displayResults(data);
    } catch (error) {
        if (error.name === 'AbortError') {
            showError('Request timeout: Processing took too long');
        } else {
            showError('Network error: ' + error.message);
        }
    } finally {
        showLoading(false);
    }
}

/**
 * Display results in table format
 * @param {Object} data - Results data from server
 */
function displayResults(data) {
    const resultsDiv = document.getElementById('resultsTable');
    const clearBtn = document.getElementById('clearBtn');
    
    if (!data.candidates || data.candidates.length === 0) {
        resultsDiv.innerHTML = '<p class="results-placeholder">No candidates found.</p>';
        clearBtn.style.display = 'none';
        return;
    }
    
    let html = '<table><thead><tr><th>Name</th><th>Email</th><th>Phone</th></tr></thead><tbody>';
    
    data.candidates.forEach(candidate => {
        html += `<tr>
            <td>${escapeHtml(candidate.name || 'N/A')}</td>
            <td>${escapeHtml(candidate.email || 'N/A')}</td>
            <td>${escapeHtml(candidate.phone || 'N/A')}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    
    // Add metadata
    html += '<div class="results-metadata">';
    html += `<p><strong>Total Candidates:</strong> ${data.candidates.length}</p>`;
    
    if (data.total_files_processed) {
        html += `<p><strong>Files Processed:</strong> ${data.total_files_processed}</p>`;
    }
    
    if (data.duplicates_removed && data.duplicates_removed > 0) {
        html += `<p><strong>Duplicates Removed:</strong> ${data.duplicates_removed}</p>`;
    }
    
    html += '</div>';
    
    // Add errors if any
    if (data.errors && data.errors.length > 0) {
        html += '<div class="error"><strong>Processing Errors:</strong><ul>';
        data.errors.forEach(error => {
            html += `<li>${escapeHtml(error)}</li>`;
        });
        html += '</ul></div>';
    }
    
    resultsDiv.innerHTML = html;
    clearBtn.style.display = 'inline-block';
}

/**
 * Show loading indicator
 * @param {boolean} show - Whether to show or hide the loading indicator
 */
function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

/**
 * Clear error message
 */
function clearError() {
    const errorDiv = document.getElementById('error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
    }
}

/**
 * Clear all results and reset interface
 */
function clearResults() {
    const resultsDiv = document.getElementById('resultsTable');
    const clearBtn = document.getElementById('clearBtn');
    const zipFile = document.getElementById('zipFile');
    const driveLink = document.getElementById('driveLink');
    const singleFile = document.getElementById('singleFile');
    
    resultsDiv.innerHTML = '<p class="results-placeholder">Results will appear here after processing</p>';
    clearBtn.style.display = 'none';
    clearError();
    
    // Reset form inputs
    zipFile.value = '';
    driveLink.value = '';
    singleFile.value = '';
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}
