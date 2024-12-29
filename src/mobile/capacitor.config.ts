import { CapacitorConfig } from '@capacitor/cli';

require("dotenv").config({
    path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

const WEBUI_URL =
  process.env.ENV == "production" && process.env.HOSTING === "hosted-global"
    ? process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL
    : process.env.LOCAL_WEBUI_SERVER_URL;

const config: CapacitorConfig = {
  appId: process.env.BUNDLE_ID,
  appName: process.env.PUBLIC_NAME,
  webDir: 'dist',
  server: {
    url: WEBUI_URL,
    cleartext: true,
    allowNavigation: [new URL(WEBUI_URL as string).hostname]
  },
  plugins: {
    SplashScreen: {
        launchAutoHide: false
    }
  }
};

export default config;
