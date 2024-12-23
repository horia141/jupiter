// eslint-disable-next-line @typescript-eslint/no-var-requires
const { app, BrowserWindow } = require("electron");
const dotEnv = require("dotenv");

loadEnvironment();

const webuiUrl =
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

  win.loadURL(webuiUrl);
}

function loadEnvironment() {
  if (app.isPackaged) {
    // If we're on MacOs
    if (process.platform === "darwin") {
      dotEnv.config({ path: app.getAppPath() + "/Config.project" });
    } else {
      console.error("Unsupported platform: ", process.platform);
      app.exit(1);
    }
  } else {
    dotEnv.config({ path: "Config.project" });
  }
}
