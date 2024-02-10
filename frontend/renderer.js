const handleAuth = async (authType, data) => {
    try {
        const response = await window.electronAPI.handleAuth(authType, data);
        console.log("Received response:", response);

        // Check for a successful message instead of 'response.success'
        if (response && (response.message === 'Login successful' || response.message === 'User registered successfully')) {            
            console.log(`${authType} successful:`, response);
            // Store username in local storage
            localStorage.setItem('username', data.username);
            window.location.href = 'dashboard.html';
        } else {
            // Handle failed login/signup
            console.error(`${authType} failed:`, response ? response.message : 'No response');
            displayAuthError('Incorrect username or password.'); // Display error for failed login
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

const displayAuthError = (message) => {
    const errorDiv = document.getElementById('authError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
};


document.getElementById('loginForm').addEventListener('submit', (event) => {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    handleAuth('login', { username, password });
});

document.getElementById('signupForm').addEventListener('submit', (event) => {
    event.preventDefault();
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newPassword').value;
    handleAuth('signup', { username, password });
});

document.getElementById('newPassword').addEventListener('input', function() {
    const strengthIndicator = document.getElementById('passwordStrengthIndicator');
    const strengthText = document.getElementById('passwordStrengthText'); // Add this line
    const strength = getPasswordStrength(this.value);

    strengthIndicator.className = 'strength-indicator';
    strengthText.textContent = ''; // Reset text

    if (strength >= 0) {
        if (strength < 3) {
            strengthIndicator.classList.add('weak');
            strengthText.textContent = 'Weak'; // Update text
        } else if (strength < 5) {
            strengthIndicator.classList.add('medium');
            strengthText.textContent = 'Medium'; // Update text
        } else {
            strengthIndicator.classList.add('strong');
            strengthText.textContent = 'Strong'; // Update text
        }
    }
});


function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 6) {
        strength++;
    }
    if (password.length >= 10) {
        strength++;
    }
    if (/[A-Z]/.test(password)) {
        strength++;
    }
    if (/[0-9]/.test(password)) {
        strength++;
    }
    if (/[^A-Za-z0-9]/.test(password)) {
        strength++;
    }
    return strength;
}

document.getElementById('passwordInfoLink').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('passwordModal').style.display = 'block';
});

// Close the modal
document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('passwordModal').style.display = 'none';
});

// Close the modal if the user clicks outside of it
window.onclick = function(event) {
    if (event.target == document.getElementById('passwordModal')) {
        document.getElementById('passwordModal').style.display = 'none';
    }
};

// Add similar event listeners and functions for storing, viewing, and deleting passwords

// ... additional code as needed
