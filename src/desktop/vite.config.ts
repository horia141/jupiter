import { resolve } from "node:path";

import { shellViteConfig } from "@jupiter/shell/vite";
import { config } from "dotenv";

config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

export default shellViteConfig({
  platform: "desktop",
  outDir: resolve(import.meta.dirname, "dist"),
  adapter: resolve(import.meta.dirname, "src/adapter.js"),
  // The pages are loaded from file://, so every URL has to be relative.
  base: "./",
  title: process.env.PUBLIC_NAME as string,
  clientVersion: process.env.VERSION as string,
  isLocal: process.env.ENV === "local",
});
