import { CapacitorConfig } from '@capacitor/cli';
import { Env, Hosting } from '../../gen/ts/webapi-client/dist';

require("dotenv").config({
    path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

const WEBUI_URL =
  process.env.ENV == Env.PRODUCTION && process.env.HOSTING === Hosting.HOSTED_GLOBAL
    ? process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL
    : process.env.LOCAL_WEBUI_SERVER_URL;

const config: CapacitorConfig = {
  appId: process.env.BUNDLE_ID,
  appName: process.env.PUBLIC_NAME,
  webDir: 'dist',
  server: {
    cleartext: process.env.ENV === Env.LOCAL ? true : false,
    allowNavigation: [new URL(WEBUI_URL as string).hostname],
    errorPath: "error.html"
  },
  ios: {
    allowsLinkPreview: false,
  },
  plugins: {
    SplashScreen: {
        launchAutoHide: false
    }
  }
};

export default config;
