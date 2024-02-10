const handleAuth = async (authType, data) => {
    try {
        const response = await window.electronAPI.handleAuth(authType, data);
        if (response && (response.message === 'Login successful' || response.message === 'User registered successfully')) {            
            localStorage.setItem('username', data.username);
            window.location.href = 'dashboard.html';
        } else {
            displayAuthError('Incorrect username or password.');
        }
    } catch (error) {
        displayAuthError('An error occurred during authentication.');
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
    const strengthText = document.getElementById('passwordStrengthText');
    const strength = getPasswordStrength(this.value);

    strengthIndicator.className = 'strength-indicator';
    strengthText.textContent = '';

    if (strength < 3) {
        strengthIndicator.classList.add('weak');
        strengthText.textContent = 'Weak';
    } else if (strength < 5) {
        strengthIndicator.classList.add('medium');
        strengthText.textContent = 'Medium';
    } else {
        strengthIndicator.classList.add('strong');
        strengthText.textContent = 'Strong';
    }
});

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 10) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
}

document.getElementById('passwordInfoLink').addEventListener('click', function(event) {
    event.preventDefault();
    document.getElementById('passwordModal').style.display = 'block';
});

document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('passwordModal').style.display = 'none';
});

window.onclick = function(event) {
    if (event.target == document.getElementById('passwordModal')) {
        document.getElementById('passwordModal').style.display = 'none';
    }
};
