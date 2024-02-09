// Import required Electron modules
const { contextBridge, ipcRenderer } = require('electron');


contextBridge.exposeInMainWorld('electron', {
    ipcRenderer: ipcRenderer
}
);

contextBridge.exposeInMainWorld('electronAPI', {
    handleAuth: (authType, data) => ipcRenderer.invoke('auth', { auth_type: authType, ...data }),
    getPasswords: (user_id) => ipcRenderer.invoke('get-passwords', user_id),
    receiveUserId: (callback) => ipcRenderer.on('user-id', (event, user_id) => callback(user_id)),

    createPassword: (data) => ipcRenderer.invoke('create-password', data),
    deletePassword: (data) => ipcRenderer.invoke('delete-password', data),
    modifyPassword: (data) => ipcRenderer.invoke('modify-password', data),
    deleteAccount: (user_id) => ipcRenderer.invoke('deleteAccount', user_id),

});

