document.getElementById('loginForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    console.log('Renderer Process - Username:', username);
    console.log('Renderer Process - Password:', password); // Mask the password in the renderer process

    // Ensure that the password is not an empty string before sending
    if (!password.trim()) {
        console.error('Renderer Process - Password is empty!');
        return;
    }

    // Send login data to the main process using ipcRenderer.invoke
    try {
        console.log('Submitting login form data:');
        const response = await electron.ipcRenderer.invoke('auth', { type: 'login', username, password });
        console.log('Login response:', response);
    } catch (error) {
        console.error('Error during login:', error);
    }
});




document.getElementById('signupForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const newUsername = document.getElementById('newUsername').value;
    const newPassword = document.getElementById('newPassword').value;

    // Send signup data to main process using ipcRenderer.invoke
    try {
        console.log('Submitting signup form data:');
        const response = await electron.ipcRenderer.invoke('auth', { type: 'signup', newUsername, newPassword });
        console.log('Signup response:', response);
    } catch (error) {
        console.error('Error during signup:', error);
    }
});


// document.getElementById('signupForm').addEventListener('submit', async (event) => {
//     event.preventDefault();
//     const newUsername = document.getElementById('newUsername').value;
//     const newPassword = document.getElementById('newPassword').value;

//     // Send signup data to main process using ipcRenderer.invoke
//     try {
//         console.log('Submitting signup form data:');
//         const response = await electron.ipcRenderer.invoke('auth', { type: 'signup', newUsername, newPassword });
//         console.log('Signup response:', response);
//     } catch (error) {
//         console.error('Error during signup:', error);
//     }
// });