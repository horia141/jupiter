// eslint-disable-next-line @typescript-eslint/no-var-requires
const { app, BrowserWindow, net, session } = require("electron");
const { AppShell } = require("@jupiter/webapi-client");
const dotEnv = require("dotenv");

loadEnvironment();

const WEBUI_URL =
  process.env.ENV == "production" && process.env.HOSTING === "hosted-global"
    ? process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL
    : process.env.LOCAL_WEBUI_SERVER_URL;

app.whenReady().then(() => {
  createWindow();

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
    width: 1200,
    height: 900,
  });

  win.loadURL(WEBUI_URL);
}

function loadEnvironment() {
  if (app.isPackaged) {
    // If we're on MacOs
    if (process.platform === "darwin") {
      dotEnv.config({ path: app.getAppPath() + "/Config.project.production" });
    } else {
      console.error("Unsupported platform: ", process.platform);
      app.exit(1);
    }
  } else {
    dotEnv.config({ path: "Config.project" });
  }
}
