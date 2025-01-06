// eslint-disable-next-line @typescript-eslint/no-var-requires
import { config } from "dotenv";
import { app, BrowserWindow, ipcMain } from "electron";
import path from "node:path";
import { fileURLToPath } from "url";

loadEnvironment();

const INITIAL_WIDTH = parseInt(process.env.INITIAL_WINDOW_WIDTH, 10);
const INITIAL_HEIGHT = parseInt(process.env.INITIAL_WINDOW_HEIGHT, 10);

app.whenReady().then(() => {
  createWindow();
  ipcMain.handle("exit", () => app.quit());

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  app.quit();
});

function createWindow() {
  const win = new BrowserWindow({
    width: INITIAL_WIDTH,
    height: INITIAL_HEIGHT,
    show: false,
    webPreferences: {
      preload: path.join(
        path.dirname(fileURLToPath(import.meta.url)),
        "src",
        "preload.js"
      ),
    },
  });

  win.loadFile("dist/index.html");
  win.webContents.on("did-fail-load", (event, errorCode, errorDescription) => {
    win.loadFile("dist/error.html");
    console.log(
      "An error occurred loading the webui: ",
      errorCode,
      errorDescription
    );
  });
  win.once("ready-to-show", () => {
    win.show();
  });
}

function loadEnvironment() {
  if (app.isPackaged) {
    // If we're on MacOs
    if (process.platform === "darwin") {
      config({
        path: [
          app.getAppPath() + "/Config.project.live",
          app.getAppPath() + "/Config.global",
        ],
      });
    } else {
      console.error("Unsupported platform: ", process.platform);
      app.exit(1);
    }
  } else {
    config({ path: ["Config.project", "../Config.global"] });
  }
}
