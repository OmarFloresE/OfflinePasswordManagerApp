const { app, BrowserWindow, ipcMain } = require('electron/main');
const path = require('node:path');
const { spawn } = require('child_process');

let win;
let globalUserId = null;

const createWindow = () => {
    win = new BrowserWindow({
        width: 800,
        height: 1000,
        webPreferences: {
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    win.loadFile('index.html');

    win.webContents.on('did-finish-load', () => {
        if (globalUserId && win.webContents.getURL().endsWith('dashboard.html')) {
            win.webContents.send('user-id', globalUserId);
        }
    });

    win.on('closed', () => {
        win = null;
    });
};

const executePythonScript = (args, callback) => {
    const pythonExecutable = 'python';
    const scriptPath = path.join(__dirname, '..', 'backend', 'main.py');
    const pythonProcess = spawn(pythonExecutable, [scriptPath, ...args], { cwd: path.join(__dirname, '..', 'backend') });

    let scriptOutput = '';
    pythonProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return callback({ success: false, error: 'Python script execution failed' });
        }
        try {
            const output = JSON.parse(scriptOutput);
            callback(output);
        } catch (error) {
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

        if (auth_type === undefined) {
            return resolve({ success: false, error: 'auth_type is undefined' });
        }

        executePythonScript(args, (output) => {
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
        executePythonScript(args, resolve);
    });
});

ipcMain.handle('create-password', async (event, data) => {
    let args = [
        `--auth_type=store`, 
        `--user_id=${data.user_id}`,
        `--website=${data.website}`,
        `--username=${data.username}`,
        `--password=${data.password}`,
        `--url=${data.url}`,
        `--description=${data.description}`,
        `--category=${data.category}`
    ];
    return new Promise((resolve) => {
        executePythonScript(args, resolve);
    });
});

ipcMain.handle('delete-password', async (event, { user_id, entryId }) => {
    let args = [`--auth_type=delete`, `--user_id=${user_id}`, `--entry_id=${entryId}`];
    return new Promise((resolve) => {
        executePythonScript(args, resolve);
    });
});

ipcMain.handle('modify-password', async (event, data) => {
    let args = [
        `--auth_type=modify`,
        `--entry_id=${data.id}`,
        `--user_id=${data.user_id}`,
        `--website=${data.website}`,
        `--username=${data.username}`,
        `--password=${data.password}`,
        `--url=${data.url}`,
        `--description=${data.description}`,
        `--category=${data.category}`
    ];
    return new Promise((resolve) => {
        executePythonScript(args, resolve);
    });
});

ipcMain.handle('deleteAccount', async (event, user_id) => {
    let args = [`--auth_type=deleteAccount`, `--user_id=${user_id}`];
    return new Promise((resolve) => {
        executePythonScript(args, resolve);
    });
});

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
