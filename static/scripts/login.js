/**
 * Priority Care - Login Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        // Attach real-time validation
        attachRealTimeValidation();
        
        // Handle form submission
        loginForm.addEventListener('submit', handleLogin);
    }
});

/**
 * Handle login form submission
 */
function handleLogin(e) {
    e.preventDefault();
    
    // Clear previous errors
    clearAllErrors();
    
    // Get form values
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    
    // Validate fields
    let isValid = true;
    
    if (!email) {
        showError('email', 'Email is required');
        isValid = false;
    } else if (!isValidEmail(email)) {
        showError('email', 'Please enter a valid email address');
        isValid = false;
    }
    
    if (!password) {
        showError('password', 'Password is required');
        isValid = false;
    } else if (password.length < 6) {
        showError('password', 'Password must be at least 6 characters');
        isValid = false;
    }
    
    if (!isValid) {
        return;
    }
    
    // In a real application, this would make an API call to authenticate
    // For now, we'll simulate a successful login for any valid email/password
    console.log('Login attempt:', { email, password: '***' });
    
    // Simulate API delay
    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Signing In...';
    
    setTimeout(() => {
        // Redirect to dashboard
        window.location.href = 'dashboard.html';
    }, 800);
}
