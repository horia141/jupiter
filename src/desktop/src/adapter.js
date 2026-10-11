// The desktop (Electron) adapter for the shared shell pages in
// @jupiter/shell. Everything goes through the main process, which owns the
// saved server and runs the server check (see src/preload.js and main.js).

export const canExit = true;

export async function exit() {
  await window.lifecycle.exit();
}

export async function init() {}

export function getServerInfo() {
  return window.pickServer.getServerInfo();
}

export function getWebUiUrl({ hostedGlobal }) {
  return window.pickServer.getWebUiUrl({ hostedGlobal });
}

export function checkServer(input) {
  return window.pickServer.checkServer(input);
}

export function pickServer(input) {
  return window.pickServer.pickServer(input);
}
