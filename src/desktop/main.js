import { checkServer } from "@jupiter/shell/check-server";
import { config } from "dotenv";
import { BrowserWindow, app, ipcMain, shell } from "electron";
import fs from "fs";
import path from "node:path";
import { fileURLToPath } from "url";

loadEnvironment();

const APP_CONFIG_PATH = "thrive.config";

const FRONTDOOR_PATTERN = process.env.FRONTDOOR_PATTERN;
const VERSION = process.env.VERSION;
const HOSTED_GLOBAL_WEBUI_URL = process.env.HOSTED_GLOBAL_WEBUI_URL;
const INITIAL_WIDTH = parseInt(process.env.INITIAL_WINDOW_WIDTH, 10);
const INITIAL_HEIGHT = parseInt(process.env.INITIAL_WINDOW_HEIGHT, 10);
const DISTRIBUTION = process.env.DISTRIBUTION;
// Plain http:// servers are only for local development. A packaged app ships
// the repo's Config.global, whose ENV is always local, so we can't go by ENV.
const ALLOW_HTTP = !app.isPackaged;
// Development runs are always aimed at a specific instance (run:desktop sets
// HOSTED_GLOBAL_WEBUI_URL), and local instances change ports between runs, so
// a server picked in one would go stale. They start on the instance they were
// given, and a server picked in them lasts only until the app quits.
const PERSIST_SERVER = app.isPackaged;

// The picked server. The official one is never saved, so with no saved
// server the app follows whatever its build points at.
let serverUrl = loadServerUrl();

app.whenReady().then(() => {
  const win = createWindow();
  ipcMain.handle("exit", handleLifecycleQuit);
  ipcMain.handle("getWebUiUrl", (event, options) => handleGetWebUiUrl(options));
  ipcMain.handle("getServerInfo", handleGetServerInfo);
  ipcMain.handle("openPicker", () => handleOpenPicker(win));
  ipcMain.handle("checkServer", (event, serverUrlString) =>
    handleCheckServer(serverUrlString),
  );
  ipcMain.handle("pickServer", (event, serverUrlString) =>
    handlePickServer(win, serverUrlString),
  );

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
        "preload.js",
      ),
    },
  });

  win.loadFile("dist/index.html");

  win.webContents.on(
    "did-fail-load",
    (event, errorCode, errorDescription, validatedURL, isMainFrame) => {
      // ERR_ABORTED (-3) means the load was superseded by another navigation,
      // and subframe failures don't take the app down, so neither is an error.
      if (!isMainFrame || errorCode === -3) {
        return;
      }

      console.error(
        "An error occurred loading the webui: ",
        errorCode,
        errorDescription,
        validatedURL,
      );
      win.loadFile("dist/error.html", {
        query: {
          reason: "navigation",
          code: String(errorCode),
          detail: errorDescription,
          url: validatedURL,
        },
      });
    },
  );
  // A server that answers with a 5xx is as broken as one that doesn't answer.
  win.webContents.on("did-navigate", (event, url, httpResponseCode) => {
    if (url.startsWith("file:") || httpResponseCode < 500) {
      return;
    }

    console.error("The webui answered with an error: ", httpResponseCode, url);
    win.loadFile("dist/error.html", {
      query: { reason: "http", code: String(httpResponseCode), url },
    });
  });
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  win.once("ready-to-show", () => {
    win.show();
  });

  return win;
}

function loadEnvironment() {
  if (app.isPackaged) {
    // If we're on MacOs
    if (process.platform === "darwin") {
      config({
        path: [
          app.getAppPath() + "/Config.project",
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

function appConfigPath() {
  return path.join(app.getPath("userData"), APP_CONFIG_PATH);
}

function loadServerUrl() {
  if (!PERSIST_SERVER) {
    return HOSTED_GLOBAL_WEBUI_URL;
  }

  try {
    if (fs.existsSync(appConfigPath())) {
      const config = JSON.parse(fs.readFileSync(appConfigPath(), "utf8"));
      // Older versions saved the official server too; treat that as unset.
      if (
        config.remoteHostWebUiUrl &&
        !isHostedGlobal(config.remoteHostWebUiUrl)
      ) {
        return config.remoteHostWebUiUrl;
      }
    }
  } catch (error) {
    console.error("Invalid config file", error);
  }

  return HOSTED_GLOBAL_WEBUI_URL;
}

function saveServerUrl(newServerUrl) {
  serverUrl = newServerUrl;
  if (!PERSIST_SERVER) {
    return;
  }

  if (isHostedGlobal(newServerUrl)) {
    fs.rmSync(appConfigPath(), { force: true });
  } else {
    fs.writeFileSync(
      appConfigPath(),
      JSON.stringify({ version: "v1", remoteHostWebUiUrl: newServerUrl }),
    );
  }
}

function isHostedGlobal(url) {
  return new URL(url).origin === new URL(HOSTED_GLOBAL_WEBUI_URL).origin;
}

function handleLifecycleQuit() {
  app.quit();
}

function handleGetWebUiUrl({ hostedGlobal } = {}) {
  return buildFrontdoor(
    hostedGlobal ? HOSTED_GLOBAL_WEBUI_URL : serverUrl,
  ).toString();
}

function handleGetServerInfo() {
  return { serverUrl, hostedGlobalUrl: HOSTED_GLOBAL_WEBUI_URL };
}

function handleOpenPicker(win) {
  // The picker lives in the app itself, so it's reachable even when the
  // picked server is down.
  win.loadFile("dist/pick-server.html");
}

function handleCheckServer(serverUrlString) {
  return checkServerFromMain(serverUrlString);
}

async function handlePickServer(win, serverUrlString) {
  const res = await checkServerFromMain(serverUrlString);
  if (res.result === "error") {
    return res;
  }

  saveServerUrl(res.serverUrl);
  win.loadURL(buildFrontdoor(res.serverUrl).toString());
  return res;
}

function checkServerFromMain(serverUrlString) {
  return checkServer(serverUrlString, {
    httpGet,
    allowHttp: ALLOW_HTTP,
    clientVersion: VERSION,
  });
}

// Node's fetch, with redirects left unfollowed so the check can see them.
async function httpGet(url) {
  const response = await fetch(url, { redirect: "manual" });
  return {
    status: response.status,
    headers: Object.fromEntries(response.headers),
  };
}

function buildFrontdoor(remoteHostWebUiUrl) {
  const frontDoorUrl = new URL(FRONTDOOR_PATTERN, remoteHostWebUiUrl);
  frontDoorUrl.searchParams.set("clientVersion", VERSION);
  frontDoorUrl.searchParams.set("initialWindowWidth", INITIAL_WIDTH);
  frontDoorUrl.searchParams.set("appDistribution", DISTRIBUTION);
  return frontDoorUrl;
}
