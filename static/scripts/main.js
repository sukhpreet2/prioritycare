/**
 * Priority Care - Main JavaScript
 * Shared utility functions and global event handlers
 */

// ============================================
// GLOBAL FUNCTIONS
// ============================================

/**
 * Logout function - redirects to login page
 */
function logout() {
    if (confirm('Are you sure you want to log out?')) {
        // In a real application, this would clear session/token
        window.location.href = 'index.html';
    }
}

/**
 * Display error message for a form field
 */
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorElement = document.getElementById(fieldId + 'Error');
    
    if (field && errorElement) {
        field.classList.add('error');
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}

/**
 * Clear error message for a form field
 */
function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorElement = document.getElementById(fieldId + 'Error');
    
    if (field && errorElement) {
        field.classList.remove('error');
        errorElement.textContent = '';
        errorElement.classList.remove('show');
    }
}

/**
 * Clear all form errors
 */
function clearAllErrors() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(error => {
        error.textContent = '';
        error.classList.remove('show');
    });
    
    const errorFields = document.querySelectorAll('.error');
    errorFields.forEach(field => {
        field.classList.remove('error');
    });
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate number is within range
 */
function isInRange(value, min, max) {
    const num = parseFloat(value);
    return !isNaN(num) && num >= min && num <= max;
}

/**
 * Show modal
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

/**
 * Hide modal
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

/**
 * Format date to readable string
 */
function formatDate(date) {
    return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Get query parameter from URL
 */
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Show success message (toast notification)
 */
function showSuccess(message) {
    // Simple alert for now - can be enhanced with custom toast notifications
    alert(message);
}

/**
 * Show error message (toast notification)
 */
function showErrorMessage(message) {
    // Simple alert for now - can be enhanced with custom toast notifications
    alert('Error: ' + message);
}

// ============================================
// PAGE LOAD HANDLERS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Close modals when clicking outside
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
    
    // Add animation to page load
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    }, 10);
});

// ============================================
// FORM VALIDATION HELPERS
// ============================================

/**
 * Real-time validation for input fields
 */
function attachRealTimeValidation() {
    const inputs = document.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });
}

/**
 * Validate individual field
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldId = field.id;
    const type = field.type;
    const required = field.hasAttribute('required');
    
    // Clear previous errors
    clearError(fieldId);
    
    // Check if required field is empty
    if (required && !value) {
        showError(fieldId, 'This field is required');
        return false;
    }
    
    // Type-specific validation
    if (value) {
        if (type === 'email' && !isValidEmail(value)) {
            showError(fieldId, 'Please enter a valid email address');
            return false;
        }
        
        if (type === 'number') {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            
            if (min !== null && max !== null) {
                if (!isInRange(value, parseFloat(min), parseFloat(max))) {
                    showError(fieldId, `Value must be between ${min} and ${max}`);
                    return false;
                }
            }
        }
    }
    
    return true;
}

/**
 * Validate entire form
 */
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}
