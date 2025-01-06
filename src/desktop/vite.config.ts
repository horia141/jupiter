import { Env, Hosting } from "@jupiter/webapi-client";
import { config } from "dotenv";
import { defineConfig } from "vite";
import handlebars from "vite-plugin-handlebars";

config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

const WEBUI_URL =
  process.env.ENV == Env.PRODUCTION &&
  process.env.HOSTING === Hosting.HOSTED_GLOBAL
    ? process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL
    : process.env.LOCAL_WEBUI_SERVER_URL;

export default defineConfig({
  root: "./src", // Source folder
  base: "./",
  build: {
    outDir: "../dist", // Output folder
    emptyOutDir: true, // Clean the output folder before building
    rollupOptions: {
      input: ["./src/splash.html", "./src/error.html"],
      preserveEntrySignatures: "strict",
    },
  },
  plugins: [
    handlebars({
      context: {
        title: process.env.PUBLIC_NAME,
        webUiUrl: WEBUI_URL,
        appShellVersion: process.env.VERSION,
      },
    }),
  ],
});
