const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("globalProperties", {
  webUiServerUrl: () => ipcRenderer.invoke("getWebUiServerUrl"),
  exit: () => ipcRenderer.invoke("exit"),
});
