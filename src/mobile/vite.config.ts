import { resolve } from "node:path";

import { shellViteConfig } from "@jupiter/shell/vite";
import { config } from "dotenv";

import { Env } from "../../gen/ts/webapi-client/dist/index.js";

config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

let hostedGlobalWebUiUrl = process.env.HOSTED_GLOBAL_WEBUI_URL as string;
if (process.env.ENV === Env.LOCAL && process.env.BUILD_TARGET === "android") {
  hostedGlobalWebUiUrl = hostedGlobalWebUiUrl.replace("localhost", "10.0.2.2");
}

export default shellViteConfig({
  platform: "mobile",
  outDir: resolve(import.meta.dirname, "dist"),
  adapter: resolve(import.meta.dirname, "src/adapter.js"),
  base: "/",
  title: process.env.PUBLIC_NAME as string,
  clientVersion: process.env.VERSION as string,
  isLocal: process.env.ENV === Env.LOCAL,
  config: {
    hostedGlobalWebUiUrl,
    frontDoorPattern: process.env.FRONTDOOR_PATTERN,
  },
});
