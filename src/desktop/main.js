// eslint-disable-next-line @typescript-eslint/no-var-requires
import { sanitizeUrl } from "@braintree/sanitize-url";
import { config } from "dotenv";
import { BrowserWindow, app, ipcMain, shell } from "electron";
import fs from "fs";
import path from "node:path";
import normalizeUrl from "normalize-url";
import semver from "semver";
import { fileURLToPath } from "url";

loadEnvironment();

const APP_CONFIG_PATH = "thrive.config";
const VERSION_HEADER = "X-Jupiter-Version";

const APP_CONFIG = loadAppConfig(APP_CONFIG_PATH);

const INITIAL_WIDTH = parseInt(process.env.INITIAL_WINDOW_WIDTH, 10);
const INITIAL_HEIGHT = parseInt(process.env.INITIAL_WINDOW_HEIGHT, 10);

app.whenReady().then(() => {
  const win = createWindow();
  ipcMain.handle("exit", handleLifecycleQuit);
  ipcMain.handle("getWebUiUrl", handleGetWebUiUrl);
  ipcMain.handle("getHostedGlobalWebUiUrl", handleGetHostedGlobalWebUiUrl);
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

  win.webContents.on("did-fail-load", (event, errorCode, errorDescription) => {
    win.loadFile("dist/error.html");
    console.error(
      "An error occurred loading the webui: ",
      errorCode,
      errorDescription,
    );
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

function loadAppConfig(appConfigPath) {
  const configPath = path.join(app.getPath("userData"), appConfigPath);
  try {
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
      return {
        version: config.version,
        webUiUrl: buildFrontdoor(config.remoteHostWebUiUrl),
        hostedGlobalWebUiUrl: buildFrontdoor(
          process.env.HOSTED_GLOBAL_WEBUI_URL,
        ),
      };
    }
  } catch (error) {
    console.error("Invalid config file", error);
  }

  const frontDoorUrl = buildFrontdoor(process.env.HOSTED_GLOBAL_WEBUI_URL);

  return {
    version: "v1",
    webUiUrl: frontDoorUrl.toString(),
    hostedGlobalWebUiUrl: frontDoorUrl.toString(),
  };
}

function updateAppConfig(appConfigPath, remoteHostWebUiUrl) {
  const configPath = path.join(app.getPath("userData"), appConfigPath);
  fs.writeFileSync(
    configPath,
    JSON.stringify({
      version: "v1",
      remoteHostWebUiUrl: remoteHostWebUiUrl,
    }),
  );
}

function handleLifecycleQuit() {
  app.quit();
}

function handleGetWebUiUrl() {
  return APP_CONFIG.webUiUrl.toString();
}

function handleGetHostedGlobalWebUiUrl() {
  return APP_CONFIG.hostedGlobalWebUiUrl.toString();
}

async function handlePickServer(win, serverUrlString) {
  let urlToUse;
  try {
    let cleanUrl = normalizeUrl(sanitizeUrl(serverUrlString), {
      defaultProtocol: "http",
      stripWWW: false,
      stripAuthentication: true,
      stripHash: true,
      stripTextFragment: true,
      removeQueryParameters: true,
      removeSingleSlash: true,
    });
    if (cleanUrl === "localhost" || cleanUrl.startsWith("localhost:")) {
      cleanUrl = "http://" + cleanUrl;
    }

    urlToUse = new URL(cleanUrl);

    if (urlToUse.protocol != "http:" && urlToUse.protocol != "https:") {
      throw new Error("Protocol must be http or https");
    }
  } catch (error) {
    return {
      result: "error",
      errorMsg: error.toString(),
    };
  }

  let latestVersionResponse;
  try {
    const latestVersionUrl = new URL("apps-latest-versions", urlToUse);
    latestVersionUrl.searchParams.set("distribution", "web");

    latestVersionResponse = await fetch(latestVersionUrl, {
      redirect: "manual",
    });

    if (
      !(
        latestVersionResponse.status === 302 ||
        latestVersionResponse.status === 301
      )
    ) {
      throw new Error("The server doesn't appear to be an instance");
    }

    if (latestVersionResponse.headers.get("Location").startsWith("https://")) {
      // In production self-hosted http gets redirected to https.
      // So the first redirect doesn't do what we want, we just do it once
      // more, so we get to the proper redirect we want.
      latestVersionResponse = await fetch(
        latestVersionResponse.headers.get("Location"),
        { redirect: "manual" },
      );

      if (
        !(
          latestVersionResponse.status === 302 ||
          latestVersionResponse.status === 301
        )
      ) {
        throw new Error("The server doesn't appear to be an instance");
      }
    }
  } catch (error) {
    return {
      result: "error",
      errorMsg: error.hasOwnProperty("cause")
        ? error.cause.toString()
        : error.toString(),
    };
  }

  const remoteVersionStr = latestVersionResponse.headers.get(VERSION_HEADER);
  if (remoteVersionStr === undefined) {
    return {
      result: "error",
      errorMsg: "The server doesn't appear to be an instance - version",
    };
  }
  const remoteVersion = semver.parse(remoteVersionStr);

  if (remoteVersion === null) {
    return {
      result: "error",
      errorMsg: "The server doesn't appear to be an instance - version format",
    };
  }
  const localVersion = semver.parse(process.env.VERSION);

  if (localVersion.major !== remoteVersion.major) {
    return {
      result: "error",
      errorMsg: `Local version ${localVersion} is incompatible with remote ${remoteVersion}`,
    };
  }

  const redirectLocation = buildFrontdoor(urlToUse);

  win.loadURL(redirectLocation.toString());
  updateAppConfig(APP_CONFIG_PATH, urlToUse.toString());

  return {
    result: "ok",
  };
}

function buildFrontdoor(remoteHostWebUiUrl) {
  const frontDoorUrl = new URL(
    process.env.FRONTDOOR_PATTERN,
    remoteHostWebUiUrl,
  );
  frontDoorUrl.searchParams.set("clientVersion", process.env.VERSION);
  frontDoorUrl.searchParams.set(
    "initialWindowWidth",
    process.env.INITIAL_WINDOW_WIDTH,
  );
  return frontDoorUrl;
}
