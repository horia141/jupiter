import { resolve } from "node:path";

import { defineConfig } from "vite";
import handlebars from "vite-plugin-handlebars";

const PAGES_DIR = resolve(import.meta.dirname, "pages");
const PAGES = ["index.html", "error.html", "pick-server.html"];

// How long the loader waits for the server before showing the error page. A
// local dev webui can take a while on a cold start; elsewhere a server that
// can't be reached at all is reported by the native layer much sooner.
const LOCAL_LOAD_TIMEOUT_MS = 60_000;
const LOAD_TIMEOUT_MS = 10_000;

/**
 * The Vite config that builds the shared shell pages into an app's `dist`.
 *
 * @param {object} options
 * @param {"desktop" | "mobile"} options.platform
 * @param {string} options.outDir Absolute path of the app's dist directory.
 * @param {string} options.adapter Absolute path of the app's adapter module.
 * @param {string} options.base "./" for file:// pages (desktop), "/" otherwise.
 * @param {string} options.title The app's public name.
 * @param {string} options.clientVersion The app's version.
 * @param {boolean} options.isLocal Whether this is a local build.
 * @param {object} [options.config] Extra build-time settings for the adapter.
 */
export function shellViteConfig({
  platform,
  outDir,
  adapter,
  base,
  title,
  clientVersion,
  isLocal,
  config = {},
}) {
  const shellConfig = {
    ...config,
    clientVersion,
    // Plain http:// servers are only for local development.
    allowHttp: isLocal,
    loadTimeoutMs: isLocal ? LOCAL_LOAD_TIMEOUT_MS : LOAD_TIMEOUT_MS,
  };

  return defineConfig({
    root: PAGES_DIR,
    base,
    publicDir: false,
    build: {
      outDir,
      emptyOutDir: true,
      rollupOptions: {
        input: PAGES.map((page) => resolve(PAGES_DIR, page)),
      },
    },
    resolve: {
      alias: { "#adapter": adapter },
    },
    define: {
      __SHELL_CONFIG__: JSON.stringify(shellConfig),
    },
    plugins: [
      handlebars({
        context: { platform, title, allowHttp: isLocal },
      }),
    ],
  });
}
