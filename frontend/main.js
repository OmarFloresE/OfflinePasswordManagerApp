// Import required Electron modules
const { app, BrowserWindow, ipcMain } = require('electron/main');
const path = require('node:path');
const { spawn } = require('child_process');

// Declare the win variable outside the createWindow function
let win;
let globalUserId = null; // Placeholder for the logged in user's ID

// Function to create the main window of the application
const createWindow = () => {
    // Create a new browser window
    win = new BrowserWindow({
        width: 800,
        height: 1000,
        webPreferences: {
        // Specify the preload script that will be run in the renderer process
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
        }
    });

  // Load the HTML file into the window
    win.loadFile('index.html');

  // Open DevTools for debugging (remove this line in production)
  // win.webContents.openDevTools();

  // Event listener for when the window has finished loading
    win.webContents.on('did-finish-load', () => {
        console.log('Page finished loading');
  });

  // Inside the createWindow function, after loading the dashboard page
    win.webContents.on('did-finish-load', () => {
        // Check if globalUserId is set and the loaded page is dashboard.html
        if (globalUserId && win.webContents.getURL().endsWith('dashboard.html')) {
            win.webContents.send('user-id', globalUserId);
            // globalUserId = null; // Reset the globalUserId
    }
});

  // Event listener for when the window is closed
    win.on('closed', () => {
        console.log('Window closed');
        win = null; // Set win to null to dereference the window object
  });
};


/////////////////////////////////////////////////////////////////

// Function to execute Python script and handle the response
const executePythonScript = (args, callback) => {
    const pythonExecutable = 'python'; // or specific path to python
    const scriptPath = path.join(__dirname, '..', 'backend', 'main.py');
    const pythonProcess = spawn(pythonExecutable, [scriptPath, ...args],{cwd:path.join(__dirname, '..', 'backend')});

    let scriptOutput = '';
    pythonProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python Output: ${scriptOutput}`); 
        if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
            return callback({ success: false, error: 'Python script execution failed' });
        }
        try {
            const output = JSON.parse(scriptOutput);
            console.log("Resolving with output:", output);  // Add this line
            callback(output);
        } catch (error) {
            console.error('Error parsing JSON output:', error);
            callback({ success: false, error: 'Error parsing JSON output' });
        }
    });
};



ipcMain.handle('auth', async (event, data) => {
    return new Promise((resolve) => {
        const { auth_type, username, password, user_id, website } = data;
        let args = [`--auth_type=${auth_type}`];
        if (username) args.push(`--username=${username}`);
        if (password) args.push(`--password=${password}`);
        if (user_id) args.push(`--user_id=${user_id}`);
        if (website) args.push(`--website=${website}`);

        console.log("Executing Python script with args:", args);

        if (auth_type === undefined) {
            console.error("auth_type is undefined");
            return resolve({ success: false, error: 'auth_type is undefined' });
        }

    executePythonScript(args, (output) => {
        // If login/signup is successful, store the user_id
        if (data.auth_type === 'login' || data.auth_type === 'signup') {
            if (output.user_id) {
                globalUserId = output.user_id;
            }
        }
        
        resolve(output);
    });
});
});

ipcMain.handle('get-passwords', async (event, user_id) => {
    return new Promise((resolve) => {
        let args = [`--auth_type=view`, `--user_id=${user_id}`];
        
        executePythonScript(args, (output) => {
            console.log("Fetched passwords:", output); // Log the output for debugging
            resolve(output);
        });
    });
});

ipcMain.handle('create-password', async (event, data) => {
    let args = [
        `--auth_type=store`, 
        `--user_id=${data.user_id}`,
        `--website=${data.website}`,
        `--username=${data.username}`,
        `--password=${data.password}`,
        `--url=${data.url}`, // Add these new lines
        `--description=${data.description}`,
        `--category=${data.category}`
    ];
    
    return new Promise((resolve) => {
        executePythonScript(args, (output) => {
            console.log("Create password response:", output); // Add this log for debugging
            resolve(output);
        });
    });
});

ipcMain.handle('delete-password', async (event, { user_id, entryId }) => {
    let args = [`--auth_type=delete`, `--user_id=${user_id}`, `--entry_id=${entryId}`];
    
    return new Promise((resolve) => {
        executePythonScript(args, (output) => {
            resolve(output);
        });
    });
});

ipcMain.handle('modify-password', async (event, data) => {
    let args = [
        `--auth_type=modify`,
        `--entry_id=${data.id}`, // ID of the entry to be modified
        `--user_id=${data.user_id}`,
        `--website=${data.website}`,
        `--username=${data.username}`,
        `--password=${data.password}`,
        `--url=${data.url}`,
        `--description=${data.description}`,
        `--category=${data.category}`
    ];

    return new Promise((resolve) => {
        executePythonScript(args, (output) => {
            console.log("Modify password response:", output); // Log for debugging
            resolve(output);
        });
    });
});

ipcMain.handle('deleteAccount', async (event, user_id) => {
    return new Promise((resolve) => {
        let args = [`--auth_type=deleteAccount`, `--user_id=${user_id}`];
        
        executePythonScript(args, (output) => {
            resolve(output);
        });
    });
});


/////////////////////////////////////////////////////////////////

// Event listener for when the Electron app is ready
app.on('ready', () => {
    createWindow();
  });
  
  // Event listener for when all windows are closed
  app.on('window-all-closed', () => {
    // Quit the app if the platform is not macOS
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });
