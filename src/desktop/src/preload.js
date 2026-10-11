const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("lifecycle", {
  exit: () => ipcRenderer.invoke("exit"),
});

// Used by the shell's own pages through src/adapter.js, except openPicker,
// which the webui calls to get back to the picker.
contextBridge.exposeInMainWorld("pickServer", {
  getWebUiUrl: (options) => ipcRenderer.invoke("getWebUiUrl", options),
  getServerInfo: () => ipcRenderer.invoke("getServerInfo"),
  openPicker: () => ipcRenderer.invoke("openPicker"),
  checkServer: (serverUrl) => ipcRenderer.invoke("checkServer", serverUrl),
  pickServer: (serverUrl) => ipcRenderer.invoke("pickServer", serverUrl),
});
