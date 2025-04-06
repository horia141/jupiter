const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("lifecycle", {
  exit: () => ipcRenderer.invoke("exit"),
});

contextBridge.exposeInMainWorld("pickServer", {
  getWebUiUrl: () => ipcRenderer.invoke("getWebUiUrl"),
  getHostedGlobalWebUiUrl: () => ipcRenderer.invoke("getHostedGlobalWebUiUrl"),
  pickServer: (serverUrl) => ipcRenderer.invoke("pickServer", serverUrl),
});
