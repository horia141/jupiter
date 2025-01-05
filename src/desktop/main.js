// eslint-disable-next-line @typescript-eslint/no-var-requires
import { app, BrowserWindow, ipcMain } from "electron";
import dotEnv from "dotenv";
import path from "node:path";
import { fileURLToPath } from 'url';

loadEnvironment();

const INITIAL_WIDTH = 1400;
const INITIAL_HEIGHT = 900;

const WEBUI_URL =
  process.env.ENV == "production" && process.env.HOSTING === "hosted-global"
    ? new URL(process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL)
    : new URL(process.env.LOCAL_WEBUI_SERVER_URL);

WEBUI_URL.searchParams.set("initialWindowWidth", INITIAL_WIDTH);

app.whenReady().then(() => {
  createWindow();
  ipcMain.handle("getWebUiServerUrl", () => WEBUI_URL.toString());
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
      preload: path.join(path.dirname(fileURLToPath(import.meta.url)), "src", "preload.js"),
    },
  });

  const splash = new BrowserWindow({
    width: INITIAL_WIDTH,
    height: INITIAL_HEIGHT,
    frame: false,
    alwaysOnTop: true,
    show: false,
  });
  splash.loadFile("dist/splash.html");

  splash.once("ready-to-show", () => {
    splash.show();
  });

  setTimeout(() => {
    splash.destroy();
    if (win.isVisible) {
      return;
    }
    win.show();
  }, 5000);

  win.loadURL(WEBUI_URL.toString());
  win.webContents.on("did-fail-load", (event, errorCode, errorDescription) => {
    win.loadFile("dist/error.html");
    console.log(
      "An error occurred loading the webui: ",
      errorCode,
      errorDescription
    );
  });
  win.once("ready-to-show", () => {
    splash.destroy();
    win.show();
  });
}

function loadEnvironment() {
  if (app.isPackaged) {
    // If we're on MacOs
    if (process.platform === "darwin") {
      dotEnv.config({ path: app.getAppPath() + "/Config.project.live" });
    } else {
      console.error("Unsupported platform: ", process.platform);
      app.exit(1);
    }
  } else {
    dotEnv.config({ path: "Config.project" });
  }
}
