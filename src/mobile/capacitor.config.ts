import { CapacitorConfig } from "@capacitor/cli";
import { KeyboardResize } from "@capacitor/keyboard";

import { Env } from "../../gen/ts/webapi-client/dist/index.js";

require("dotenv").config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

const config: CapacitorConfig = {
  appId: process.env.BUNDLE_ID,
  appName: process.env.PUBLIC_NAME,
  webDir: "dist",
  server: {
    cleartext: process.env.ENV === Env.LOCAL ? true : false,
    // Users can pick a self-hosted server at runtime (see pick-server.html),
    // so we can't know the host at build time. This also means the bridge is
    // injected into whatever server the user picks.
    allowNavigation: ["*"],
    errorPath: "error.html",
  },
  ios: {
    allowsLinkPreview: false,
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: false,
    },
    Keyboard: {
      resize: KeyboardResize.Body, // try Body first
      resizeOnFullScreen: false, // keep false unless you truly need it
    },
  },
};

export default config;
