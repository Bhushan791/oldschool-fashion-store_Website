// main.js - JavaScript for OLDSCHOOL Fashion website

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeNotifications();
    initializeFormValidation();
    initializeQuantityHandlers();
    initializeOrderConfirmation();
    initializeAdminFunctions();
    initializePasswordStrengthMeter();
    
    // Handle flash messages (from Flask)
    handleFlashMessages();
});

// ===== NOTIFICATION SYSTEM =====
function initializeNotifications() {
    // Create notification container if it doesn't exist
    if (!document.querySelector('.notification-container')) {
        const notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
}

function showNotification(message, type = 'info') {
    const container = document.querySelector('.notification-container');
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Show with animation
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', function() {
        closeNotification(notification);
    });
    
    // Auto close after 5 seconds
    setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}

function closeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        notification.remove();
    }, 300); // Match the CSS transition time
}

// Process Flask flash messages and convert to our notification system
function handleFlashMessages() {
    const flashes = document.querySelector('.flashes');
    if (flashes) {
        const messages = flashes.querySelectorAll('.flash-message');
        messages.forEach(message => {
            // Determine message type based on content
            let type = 'info';
            if (message.textContent.toLowerCase().includes('success')) type = 'success';
            if (message.textContent.toLowerCase().includes('error') || 
                message.textContent.toLowerCase().includes('failed')) type = 'error';
            
            showNotification(message.textContent, type);
        });
        
        // Remove the original flash container
        flashes.remove();
    }
}

// ===== FORM VALIDATION =====
function initializeFormValidation() {
    // Login form validation
    const loginForm = document.querySelector('.auth-form');
    if (loginForm && loginForm.closest('.auth-form-container').querySelector('h2').textContent.includes('Log In')) {
        loginForm.addEventListener('submit', function(e) {
            const emailInput = this.querySelector('input[name="email"]');
            const passwordInput = this.querySelector('input[name="password"]');
            
            if (!validateEmail(emailInput.value)) {
                e.preventDefault();
                showFormError(emailInput, 'Please enter a valid email address');
            }
            
            if (passwordInput.value.length < 6) {
                e.preventDefault();
                showFormError(passwordInput, 'Password must be at least 6 characters');
            }
        });
        
        // Detect login errors from Flask and handle them
        checkForLoginErrors();
    }
    
    // Signup form validation
    const signupForm = document.querySelector('.auth-form');
    if (signupForm && signupForm.closest('.auth-form-container').querySelector('h2').textContent.includes('Sign Up')) {
        signupForm.addEventListener('submit', function(e) {
            const emailInput = this.querySelector('input[name="email"]');
            const passwordInput = this.querySelector('input[name="password"]');
            const confirmInput = this.querySelector('input[name="confirm_password"]');
            
            if (!validateEmail(emailInput.value)) {
                e.preventDefault();
                showFormError(emailInput, 'Please enter a valid email address');
            }
            
            if (passwordInput.value.length < 6) {
                e.preventDefault();
                showFormError(passwordInput, 'Password must be at least 6 characters');
                showNotification('Password must be at least 6 characters', 'error');
            } else if (passwordInput.value.length > 20) {
                e.preventDefault();
                showFormError(passwordInput, 'Password must be less than 20 characters');
                showNotification('Password must be less than 20 characters', 'error');
            }
            
            if (passwordInput.value !== confirmInput.value) {
                e.preventDefault();
                showFormError(confirmInput, 'Passwords do not match');
                showNotification('Passwords do not match', 'error');
            }
        });
        
        // Check for email already exists error
        checkForEmailExistsError();
    }
    
    // Add to cart form validation
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const quantityInput = this.querySelector('input[name="quantity"]');
            if (parseInt(quantityInput.value) < 1) {
                e.preventDefault();
                showFormError(quantityInput, 'Quantity must be at least 1');
            }
        });
    });
    
    // Checkout form validation
    const checkoutForm = document.querySelector('.checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            const nameInput = this.querySelector('input[name="name"]');
            const addressInput = this.querySelector('input[name="address"]');
            
            if (nameInput.value.trim().length < 3) {
                e.preventDefault();
                showFormError(nameInput, 'Please enter your full name');
            }
            
            if (addressInput.value.trim().length < 10) {
                e.preventDefault();
                showFormError(addressInput, 'Please enter your complete address');
            }
        });
    }
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showFormError(inputElement, message) {
    // Remove any existing error
    removeFormError(inputElement);
    
    // Create error message
    const errorElement = document.createElement('div');
    errorElement.className = 'form-error';
    errorElement.textContent = message;
    
    // Add error class to input
    inputElement.classList.add('input-error');
    
    // Insert error after input
    inputElement.parentNode.insertBefore(errorElement, inputElement.nextSibling);
    
    // Focus on the input
    inputElement.focus();
}

function removeFormError(inputElement) {
    // Remove error class
    inputElement.classList.remove('input-error');
    
    // Remove error message if exists
    const nextElement = inputElement.nextElementSibling;
    if (nextElement && nextElement.classList.contains('form-error')) {
        nextElement.remove();
    }
}

// ===== PASSWORD STRENGTH METER =====
function initializePasswordStrengthMeter() {
    // Add password strength meter to signup form
    const signupForm = document.querySelector('.auth-form');
    if (signupForm && signupForm.closest('.auth-form-container').querySelector('h2').textContent.includes('Sign Up')) {
        const passwordInput = signupForm.querySelector('input[name="password"]');
        
        // Create strength meter
        const strengthMeter = document.createElement('div');
        strengthMeter.className = 'password-strength-meter';
        
        // Create meter bar
        const meterBar = document.createElement('div');
        meterBar.className = 'strength-meter-bar';
        
        // Create meter text
        const meterText = document.createElement('div');
        meterText.className = 'strength-meter-text';
        meterText.textContent = 'Password strength: Too short';
        
        // Append elements
        strengthMeter.appendChild(meterBar);
        strengthMeter.appendChild(meterText);
        
        // Insert after password field
        passwordInput.parentNode.insertBefore(strengthMeter, passwordInput.nextSibling);
        
        // Add event listener
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value, meterBar, meterText);
        });
        
        // Add event listener for password field focus
        passwordInput.addEventListener('focus', function() {
            strengthMeter.style.display = 'block';
        });
        
        // Hide strength meter initially
        strengthMeter.style.display = 'none';
    }
}

function updatePasswordStrength(password, meterBar, meterText) {
    // Calculate password strength
    let strength = 0;
    const feedback = [];
    
    // Length check
    if (password.length < 6) {
        strength = 0;
        feedback.push('Too short');
    } else {
        // Start with some points for minimum length
        strength = 20;
        
        // Add length bonus (up to 20 points)
        strength += Math.min(20, password.length * 2);
        
        // Check for various character types
        if (/[A-Z]/.test(password)) {
            strength += 10;
        } else {
            feedback.push('Add uppercase letters');
        }
        
        if (/[a-z]/.test(password)) {
            strength += 10;
        } else {
            feedback.push('Add lowercase letters');
        }
        
        if (/[0-9]/.test(password)) {
            strength += 10;
        } else {
            feedback.push('Add numbers');
        }
        
        if (/[^A-Za-z0-9]/.test(password)) {
            strength += 10;
        } else {
            feedback.push('Add special characters');
        }
        
        // Check for repeated characters
        if (/(.)\1{2,}/.test(password)) {
            strength -= 10;
            feedback.push('Avoid repeated characters');
        }
    }
    
    // Cap at 100
    strength = Math.min(100, strength);
    
    // Update meter bar
    meterBar.style.width = strength + '%';
    
    // Set color based on strength
    if (strength < 30) {
        meterBar.style.backgroundColor = '#f44336'; // Red
        if (feedback.length === 0) feedback.push('Weak');
    } else if (strength < 60) {
        meterBar.style.backgroundColor = '#ff9800'; // Orange
        if (feedback.length === 0) feedback.push('Medium');
    } else if (strength < 80) {
        meterBar.style.backgroundColor = '#4caf50'; // Green
        if (feedback.length === 0) feedback.push('Strong');
    } else {
        meterBar.style.backgroundColor = '#2e7d32'; // Dark Green
        if (feedback.length === 0) feedback.push('Very strong');
    }
    
    // Update text
    meterText.textContent = 'Password strength: ' + (feedback.length > 0 ? feedback.join(', ') : 'Very strong');
}

// ===== QUANTITY HANDLERS =====
function initializeQuantityHandlers() {
    // Add quantity controls to product detail page
    const quantityInput = document.querySelector('.quantity-input');
    if (quantityInput) {
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'quantity-controls';
        
        // Create decrement button
        const decrementBtn = document.createElement('button');
        decrementBtn.type = 'button';
        decrementBtn.className = 'quantity-btn quantity-decrease';
        decrementBtn.textContent = '-';
        decrementBtn.addEventListener('click', () => {
            if (parseInt(quantityInput.value) > 1) {
                quantityInput.value = parseInt(quantityInput.value) - 1;
            }
        });
        
        // Create increment button
        const incrementBtn = document.createElement('button');
        incrementBtn.type = 'button';
        incrementBtn.className = 'quantity-btn quantity-increase';
        incrementBtn.textContent = '+';
        incrementBtn.addEventListener('click', () => {
            quantityInput.value = parseInt(quantityInput.value) + 1;
        });
        
        // Replace input with our control
        quantityInput.parentNode.insertBefore(wrapper, quantityInput);
        wrapper.appendChild(decrementBtn);
        wrapper.appendChild(quantityInput);
        wrapper.appendChild(incrementBtn);
    }
}

// ===== ORDER CONFIRMATION =====
function initializeOrderConfirmation() {
    // Add confirmation to checkout form
    const checkoutForm = document.querySelector('.checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to place this order?')) {
                e.preventDefault();
            } else {
                showNotification('Order placed successfully! Thank you for your purchase.', 'success');
            }
        });
    }
    
    // Add confirmation to cancel order buttons
    const cancelOrderForms = document.querySelectorAll('.cancel-form');
    cancelOrderForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to cancel this order?')) {
                e.preventDefault();
            } else {
                showNotification('Order has been cancelled.', 'info');
            }
        });
    });
    
    // Add confirmation to remove from cart links
    const removeLinks = document.querySelectorAll('.remove-link');
    removeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Remove this item from your cart?')) {
                e.preventDefault();
            }
        });
    });
}

// ===== ADMIN FUNCTIONS =====
function initializeAdminFunctions() {
    // Admin panel delete confirmation
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        // We'll still use the onclick attribute for the main confirmation,
        // but we can enhance it with a notification after it's clicked
        button.addEventListener('click', function(e) {
            // The actual confirmation is handled by the onclick attribute
            // This will only run if user confirmed
            setTimeout(() => {
                showNotification('Product deleted successfully.', 'info');
            }, 500);
        });
    });
    
    // Admin order status update
    const statusForms = document.querySelectorAll('.status-form');
    statusForms.forEach(form => {
        const select = form.querySelector('.status-select');
        const originalValue = select.value;
        
        form.addEventListener('submit', function(e) {
            if (select.value !== originalValue) {
                if (!confirm(`Change order status to ${select.value}?`)) {
                    e.preventDefault();
                } else {
                    showNotification(`Order status updated to ${select.value}.`, 'success');
                }
            }
        });
    });
    
    // Product form validation and image preview
    const productForm = document.querySelector('.admin-form');
    if (productForm) {
        // Image preview
        const imageInput = productForm.querySelector('input[type="file"]');
        if (imageInput) {
            // Create preview container
            const previewContainer = document.createElement('div');
            previewContainer.className = 'image-preview-container';
            previewContainer.innerHTML = '<img class="image-preview" src="#" alt="Preview" style="display: none;">';
            imageInput.parentNode.appendChild(previewContainer);
            
            const previewImg = previewContainer.querySelector('.image-preview');
            
            // Show preview on file select
            imageInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                    }
                    reader.readAsDataURL(this.files[0]);
                }
            });
        }
        
        // Form validation
        productForm.addEventListener('submit', function(e) {
            const nameInput = this.querySelector('input[name="name"]');
            const priceInput = this.querySelector('input[name="price"]');
            
            if (nameInput.value.trim().length < 3) {
                e.preventDefault();
                showFormError(nameInput, 'Product name must be at least 3 characters');
            }
            
            const price = parseFloat(priceInput.value);
            if (isNaN(price) || price <= 0) {
                e.preventDefault();
                showFormError(priceInput, 'Please enter a valid price');
            }
        });
    }
}

// ===== ERROR DETECTION FUNCTIONS =====

// Check for login errors
function checkForLoginErrors() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Check for invalid credentials
    if (urlParams.has('error') && urlParams.get('error') === 'invalid_credentials') {
        showNotification('Invalid email or password', 'error');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Check for account not found
    if (urlParams.has('error') && urlParams.get('error') === 'not_found') {
        showNotification('Account not found. Please check your email or sign up', 'error');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Check if account is locked
    if (urlParams.has('error') && urlParams.get('error') === 'locked') {
        showNotification('Account is locked. Please contact support', 'error');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// Check for email already exists error
function checkForEmailExistsError() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.has('error') && urlParams.get('error') === 'email_exists') {
        const emailInput = document.querySelector('input[name="email"]');
        showFormError(emailInput, 'This email is already registered');
        showNotification('This email is already registered. Please login instead', 'error');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ===== LOGIN/LOGOUT HANDLING =====
// Check if we just logged in or out (check URL parameters)
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has('login') && urlParams.get('login') === 'success') {
    showNotification('You have successfully logged in!', 'success');
    // Clean URL
    window.history.replaceState({}, document.title, window.location.pathname);
}

if (urlParams.has('logout') && urlParams.get('logout') === 'success') {
    showNotification('You have been logged out.', 'info');
    // Clean URL
    window.history.replaceState({}, document.title, window.location.pathname);
}




document.addEventListener('DOMContentLoaded', () => {
    // Password toggle
    document.querySelectorAll('.password-toggle').forEach(toggle => {
      toggle.addEventListener('click', () => {
        const targetId = toggle.getAttribute('data-target');
        const input = document.getElementById(targetId);
        if (input.type === 'password') {
          input.type = 'text';
        } else {
          input.type = 'password';
        }
      });
    });
  });
  