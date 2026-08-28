const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openExternal: (url) => ipcRenderer.send('open-external', url),
  getCesiumPath: () => ipcRenderer.invoke('get-cesium-path'),
  platform: process.platform
});
