// Lekzy-TTP SMS Sender JavaScript

// Login functionality
function handleLogin(event) {
    event.preventDefault();
    
    const apiKey = document.getElementById('api_key').value.trim();
    const errorDiv = document.getElementById('error');
    const submitBtn = document.getElementById('submit-btn');
    
    if (!apiKey) {
        showError('Please enter an API key');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Validating...';
    
    // Hide error div if it exists
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
    
    // Submit form
    document.getElementById('login-form').submit();
}

// Android SMS sending
async function sendAndroidSMS() {
    const message = document.getElementById('message').value.trim();
    const phoneNumbers = document.getElementById('phone_numbers').value.trim();
    
    if (!message || !phoneNumbers) {
        showError('Please fill in all fields');
        return;
    }
    
    // Store data for sending page
    sessionStorage.setItem('androidMessage', message);
    sessionStorage.setItem('androidNumbers', phoneNumbers);
    
    // Redirect to sending status page
    window.location.href = '/android_sending';
}

// SMTP SMS sending
async function sendSMTPSMS() {
    const message = document.getElementById('message').value.trim();
    const phoneNumbers = document.getElementById('phone_numbers').value.trim();
    const carrierDomain = document.getElementById('carrier').value;
    
    if (!message || !phoneNumbers || !carrierDomain) {
        showError('Please fill in all fields');
        return;
    }
    
    // Store data for sending page
    sessionStorage.setItem('smtpMessage', message);
    sessionStorage.setItem('smtpNumbers', phoneNumbers);
    sessionStorage.setItem('smtpCarrier', carrierDomain);
    
    // Redirect to sending status page
    window.location.href = '/smtp_sending';
}

// Utility functions
function showError(message) {
    const errorDiv = document.getElementById('error') || createMessageDiv('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('success') || createMessageDiv('success');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 5000);
}

function createMessageDiv(type) {
    const div = document.createElement('div');
    div.id = type;
    div.className = type;
    div.style.display = 'none';
    
    const container = document.querySelector('.container');
    container.insertBefore(div, container.firstChild);
    
    return div;
}

function showLoading(show) {
    const loadingDiv = document.getElementById('loading');
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
    
    // Disable/enable send buttons
    const sendBtns = document.querySelectorAll('.btn-primary');
    sendBtns.forEach(btn => {
        btn.disabled = show;
        if (show) {
            btn.textContent = 'Sending...';
        } else {
            btn.textContent = btn.dataset.originalText || 'Send SMS';
        }
    });
}

function updateStats(sent, failed) {
    const sentElement = document.getElementById('sent-count');
    const failedElement = document.getElementById('failed-count');
    const totalElement = document.getElementById('total-count');
    
    if (sentElement) sentElement.textContent = sent;
    if (failedElement) failedElement.textContent = failed;
    if (totalElement) totalElement.textContent = sent + failed;
}

// Phone number validation and formatting
function validatePhoneNumbers() {
    const textarea = document.getElementById('phone_numbers');
    const phoneNumbers = textarea.value;
    
    // Split by lines and commas, clean each number
    const numbers = phoneNumbers.split(/[\n,]/)
        .map(num => num.trim().replace(/\D/g, ''))
        .filter(num => num.length >= 10 && num.length <= 15);
    
    // Remove duplicates
    const uniqueNumbers = [...new Set(numbers)];
    
    // Update textarea with cleaned numbers
    textarea.value = uniqueNumbers.join('\n');
    
    // Show count
    const countDiv = document.getElementById('number-count');
    if (countDiv) {
        countDiv.textContent = `${uniqueNumbers.length} valid numbers`;
    }
}

// Auto-save form data to localStorage
function saveFormData(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (key !== 'smtp_password') { // Don't save passwords
            data[key] = value;
        }
    }
    
    localStorage.setItem(formId + '_data', JSON.stringify(data));
}

function loadFormData(formId) {
    const savedData = localStorage.getItem(formId + '_data');
    if (!savedData) return;
    
    try {
        const data = JSON.parse(savedData);
        
        for (let [key, value] of Object.entries(data)) {
            const element = document.getElementById(key);
            if (element) {
                element.value = value;
            }
        }
    } catch (error) {
        console.error('Error loading form data:', error);
    }
}

// Initialize page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Store original button text for loading states
    const buttons = document.querySelectorAll('.btn-primary');
    buttons.forEach(btn => {
        btn.dataset.originalText = btn.textContent;
    });
    
    // Load saved form data
    const forms = document.querySelectorAll('form[id]');
    forms.forEach(form => {
        loadFormData(form.id);
        
        // Auto-save on input
        form.addEventListener('input', () => {
            saveFormData(form.id);
        });
    });
    
    // Phone number validation on input
    const phoneTextarea = document.getElementById('phone_numbers');
    if (phoneTextarea) {
        phoneTextarea.addEventListener('blur', validatePhoneNumbers);
    }
    
    // Focus first input on page load
    const firstInput = document.querySelector('input[type="text"], input[type="password"], textarea');
    if (firstInput) {
        firstInput.focus();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit forms
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const submitBtn = document.querySelector('.btn-primary:not(:disabled)');
        if (submitBtn) {
            submitBtn.click();
        }
    }
    
    // Escape to go back
    if (event.key === 'Escape') {
        const backBtn = document.querySelector('.back-btn');
        if (backBtn) {
            backBtn.click();
        }
    }
});
