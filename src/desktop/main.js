// eslint-disable-next-line @typescript-eslint/no-var-requires
const { app, BrowserWindow, net, session } = require("electron");
const { AppShell } = require("@jupiter/webapi-client");
const dotEnv = require("dotenv");

loadEnvironment();

const INITIAL_WIDTH = 1200;
const INITIAL_HEIGHT = 900;

const WEBUI_URL =
  process.env.ENV == "production" && process.env.HOSTING === "hosted-global"
    ? new URL(process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL)
    : new URL(process.env.LOCAL_WEBUI_SERVER_URL);

WEBUI_URL.searchParams.set("initialWindowWidth", INITIAL_WIDTH);

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
    width: INITIAL_WIDTH,
    height: INITIAL_HEIGHT,
  });

  win.loadURL(WEBUI_URL.toString());
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
