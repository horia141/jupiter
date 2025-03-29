import { CapacitorConfig } from "@capacitor/cli";
import { Env, Hosting } from "../../gen/ts/webapi-client/dist";

require("dotenv").config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

let hostedGlobalWebUiUrl = process.env.HOSTED_GLOBAL_WEBUI_URL as string;
if (process.env.ENV === Env.LOCAL && process.env.BUILD_TARGET === "android") {
  hostedGlobalWebUiUrl = hostedGlobalWebUiUrl.replace("localhost", "10.0.2.2");
}

const config: CapacitorConfig = {
  appId: process.env.BUNDLE_ID,
  appName: process.env.PUBLIC_NAME,
  webDir: "dist",
  server: {
    cleartext: process.env.ENV === Env.LOCAL ? true : false,
    allowNavigation: [new URL(hostedGlobalWebUiUrl).hostname],
    errorPath: "error.html",
  },
  ios: {
    allowsLinkPreview: false,
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: false,
    },
  },
};

export default config;
