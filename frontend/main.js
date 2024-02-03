// Import required Electron modules
const { app, BrowserWindow, ipcMain } = require('electron/main');
const path = require('node:path');
const { spawn } = require('child_process');

// Declare the win variable outside the createWindow function
let win;

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

  // Event listener for when the window is closed
  win.on('closed', () => {
    console.log('Window closed');
    win = null; // Set win to null to dereference the window object
  });
};


/////////////////////////////////////////////////////////////////

// Function to listen to an event once
const once = (emitter, event) => {
    return new Promise((resolve) => {
        emitter.once(event, resolve);
    });
};

// const util = require('util');
// const { execFile } = require('child_process');

// const executePythonScript = async (event, scriptArgs) => {
//     try {
//         const pythonScriptPath = path.join(__dirname, '..', 'backend', 'main.py');
//         console.log('Executing Python script with args:', scriptArgs);
//         console.log('Python Script Path:', pythonScriptPath);
//         const { stdout, stderr } = await util.promisify(execFile)('python', [pythonScriptPath, ...scriptArgs], { cwd: path.join(__dirname, '..', 'backend') });
//         event.sender.send('response', { success: true, output: stdout });
//     } catch (error) {
//         console.error(`Python Error: ${error}`);
//         event.sender.send('response', { success: false, error: error.toString() });
//     }
// };


ipcMain.handle('login', async (event, data) => {
    const { username, password } = data;

    try {
        // const pythonExecutable = 'C:/Users/OmarF/AppData/Local/Programs/Python/Python312/python.exe'; // Windows        
        const pythonExecutable = 'python'; // Just 'python' assuming it's in the system's PATH
        const pythonScriptPath = path.join(__dirname, '..', 'backend', 'main.py');
        const pythonProcess = spawn(pythonExecutable, [pythonScriptPath, username, password, 'login'], { cwd: path.join(__dirname, '..', 'backend') });

        const stdoutPromise = new Promise((resolve) => {
            pythonProcess.stdout.once('data', (data) => resolve(data));
        });

        const stderrPromise = new Promise((resolve) => {
            pythonProcess.stderr.once('data', (data) => resolve(data));
        });

        const [stdout, stderr] = await Promise.all([stdoutPromise, stderrPromise]);
        console.log(`Python Output (stdout): ${stdout}`);
        console.log(`Python Output (stderr): ${stderr}`);
        // Handle Python script output
        console.log(`Python Output: ${stdout}`);
        event.reply('response', { success: true, output: stdout });
    } catch (error) {
        // Handle errors from Python script
        console.error(`Python Error: ${error}`);
        event.reply('response', { success: false, error: error.toString() });
    }
});

ipcMain.handle('signup', async (event, data) => {
    const { newUsername, newPassword } = data;

    try {
        // const pythonExecutable = 'C:/Users/OmarF/AppData/Local/Programs/Python/Python312/python.exe'; // Windows
        const pythonExecutable = 'python'; // Just 'python' assuming it's in the system's PATH
        const pythonScriptPath = path.join(__dirname, '..', 'backend', 'main.py');

        const pythonProcess = spawn(pythonExecutable, [pythonScriptPath, newUsername, newPassword, 'signup'], { cwd: path.join(__dirname, '..', 'backend') });        const stdoutPromise = new Promise((resolve) => {
        pythonProcess.stdout.once('data', (data) => resolve(data));
        });

        const stderrPromise = new Promise((resolve) => {
            pythonProcess.stderr.once('data', (data) => resolve(data));
        });

        const [stdout, stderr] = await Promise.all([stdoutPromise, stderrPromise]);
        console.log(`Python Output (stdout): ${stdout}`);
        console.log(`Python Output (stderr): ${stderr}`);
        // Handle Python script output
        console.log(`Python Output: ${stdout}`);
        event.reply('response', { success: true, output: stdout });
    } catch (error) {
        // Handle errors from Python script
        console.error(`Python Error: ${error}`);
        event.reply('response', { success: false, error: error.toString() });
    }
});

ipcMain.handle('auth', async (event, data) => {
    const { type, username, password, newUsername, newPassword } = data;

    if (type === 'login' || type === 'signup') {
        try {
            // Call Python script with login/signup data
            console.log('Spawning Python process...');
            const pythonExecutable = 'python'; // Windows
            const pythonScriptPath = path.join(__dirname, '..', 'backend', 'main.py');
            console.log('Python Script Path:', pythonScriptPath);

            const pythonProcess = spawn(pythonExecutable, [pythonScriptPath, type === 'login' ? username : newUsername, type === 'signup' ? newPassword : password, type],{ cwd: path.join(__dirname, '..', 'backend') });

            pythonProcess.stdout.on('data', (data) => {
                console.log(`Python Output (stdout): ${data}`);
                event.reply('response', { success: true, output: data });
            });

            pythonProcess.stderr.on('data', (data) => {
                console.error(`Python Output (stderr): ${data}`);
                event.reply('response', { success: false, error: data.toString() });
            });

            pythonProcess.on('close', (code) => {
                console.log(`Python process closed with code ${code}`);
            });
        } catch (error) {
            console.error(`Python Error: ${error}`);
            event.reply('response', { success: false, error: error.toString() });
        }
    } else {
        console.error('Invalid auth request type.');
        event.reply('response', { success: false, error: 'Invalid request type.' });
    }
});


/////////////////////////////////////////////////////////////////

// Event listener for when the Electron app is ready
app.on('ready', () => {
    // Handle an IPC (Inter-Process Communication) event called 'ping'
    // The handler returns the string 'pong'
    ipcMain.handle('ping', () => 'pong');
  
    // Call the function to create the main window
    createWindow();
  });
  
  // Event listener for when all windows are closed
  app.on('window-all-closed', () => {
    // Quit the app if the platform is not macOS
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });
