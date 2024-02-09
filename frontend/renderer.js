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
        }
    } catch (error) {
        console.error('Error:', error);
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

// Add similar event listeners and functions for storing, viewing, and deleting passwords

// ... additional code as needed
