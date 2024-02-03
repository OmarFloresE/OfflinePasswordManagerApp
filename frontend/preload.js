// Import required Electron modules
const { contextBridge, ipcRenderer } = require('electron');


contextBridge.exposeInMainWorld('electron', {
    ipcRenderer: ipcRenderer
}
);

