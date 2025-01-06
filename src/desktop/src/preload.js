const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("preload", {
  exit: () => ipcRenderer.invoke("exit"),
});
