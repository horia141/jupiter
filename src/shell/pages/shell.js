/**
 * What the shared pages know about the shell they run in.
 *
 * Every platform-specific call goes through the adapter, which each app's
 * Vite build aliases to its own module as "#adapter". An adapter exports:
 *
 * - `init()`: anything to do once a page loads (e.g. hide the splash screen).
 * - `getServerInfo()`: `{ serverUrl, hostedGlobalUrl }`, the picked server
 *   and the official one.
 * - `getWebUiUrl({ hostedGlobal })`: the frontdoor URL to load, for the picked
 *   server or, with `hostedGlobal`, the official one.
 * - `checkServer(input)`: the shared check from `lib/check-server.js`, run
 *   with the platform's HTTP client.
 * - `pickServer(input)`: checks, saves and loads a server; resolves to an
 *   error result if the check fails.
 * - `canExit` and `exit()`: whether the app can be quit from a page.
 */

/** Build-time settings, from the app's Vite config. */
export const SHELL_CONFIG = __SHELL_CONFIG__;

export function isSameOrigin(a, b) {
  return new URL(a).origin === new URL(b).origin;
}
