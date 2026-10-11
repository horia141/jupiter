// The mobile (Capacitor) adapter for the shared shell pages in @jupiter/shell.

import { Capacitor, CapacitorHttp } from "@capacitor/core";
import { Device } from "@capacitor/device";
import { Preferences } from "@capacitor/preferences";
import { SplashScreen } from "@capacitor/splash-screen";
import { checkServer as checkServerWith } from "@jupiter/shell/check-server";

import { AppDistribution } from "../../../gen/ts/webapi-client/gen/models/AppDistribution";
import { AppPlatform } from "../../../gen/ts/webapi-client/gen/models/AppPlatform";

const CONFIG = __SHELL_CONFIG__;
// No entry means the official server, so a build always follows its own.
const SERVER_URL_KEY = "serverUrl";

export const canExit = false;

export async function exit() {}

export async function init() {
  await SplashScreen.hide();
}

export async function getServerInfo() {
  const { value } = await Preferences.get({ key: SERVER_URL_KEY });
  return {
    serverUrl: value ?? CONFIG.hostedGlobalWebUiUrl,
    hostedGlobalUrl: CONFIG.hostedGlobalWebUiUrl,
  };
}

export async function getWebUiUrl({ hostedGlobal }) {
  const { serverUrl, hostedGlobalUrl } = await getServerInfo();
  const asUrl = new URL(
    CONFIG.frontDoorPattern,
    hostedGlobal ? hostedGlobalUrl : serverUrl,
  );

  const deviceType = await checkDeviceType();

  asUrl.searchParams.set("clientVersion", CONFIG.clientVersion);

  if (Capacitor.getPlatform() === "ios") {
    if (deviceType === "tablet") {
      asUrl.searchParams.set("appPlatform", AppPlatform.TABLET_IOS);
    } else {
      asUrl.searchParams.set("appPlatform", AppPlatform.MOBILE_IOS);
    }
    asUrl.searchParams.set("appDistribution", AppDistribution.APP_STORE);
  } else if (Capacitor.getPlatform() === "android") {
    if (deviceType === "tablet") {
      asUrl.searchParams.set("appPlatform", AppPlatform.TABLET_ANDROID);
    } else {
      asUrl.searchParams.set("appPlatform", AppPlatform.MOBILE_ANDROID);
    }
    asUrl.searchParams.set(
      "appDistribution",
      AppDistribution.GOOGLE_PLAY_STORE,
    );
  }

  return asUrl.toString();
}

export function checkServer(input) {
  return checkServerWith(input, {
    httpGet,
    allowHttp: CONFIG.allowHttp,
    clientVersion: CONFIG.clientVersion,
  });
}

export async function pickServer(input) {
  const res = await checkServer(input);
  if (res.result === "error") {
    return res;
  }

  if (
    new URL(res.serverUrl).origin ===
    new URL(CONFIG.hostedGlobalWebUiUrl).origin
  ) {
    await Preferences.remove({ key: SERVER_URL_KEY });
  } else {
    await Preferences.set({ key: SERVER_URL_KEY, value: res.serverUrl });
  }
  window.location.href = "index.html";
  return res;
}

// CapacitorHttp goes through the native HTTP stack, so it isn't subject to
// CORS and can leave redirects unfollowed.
async function httpGet(url) {
  const response = await CapacitorHttp.get({ url, disableRedirects: true });
  return { status: response.status, headers: response.headers ?? {} };
}

async function checkDeviceType() {
  const info = await Device.getInfo();

  if (info.platform === "ios") {
    // On iOS, check the model or other properties
    return info.model?.includes("iPad") ? "tablet" : "phone";
  } else if (info.platform === "android") {
    // On Android, use heuristic methods
    const isTablet = await isAndroidTablet(info);
    return isTablet ? "tablet" : "phone";
  } else {
    return "unknown"; // Web or other platforms
  }
}

async function isAndroidTablet(info) {
  const width = window.screen.width;
  const height = window.screen.height;
  const dpi = window.devicePixelRatio;

  const screenSizeInInches = Math.sqrt(
    (width / dpi) ** 2 + (height / dpi) ** 2,
  );

  return screenSizeInInches >= 7; // Heuristic: 7 inches or larger is considered a tablet
}
