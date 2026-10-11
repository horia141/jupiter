/**
 * Building and reading the error page's query string, shared by every way a
 * shell can end up on it: the loader timing out, the native layer failing a
 * navigation, or the server answering with a 5xx.
 */

export const ErrorReason = Object.freeze({
  // The loader gave up waiting for the server. `detail` = seconds waited.
  TIMEOUT: "timeout",
  // The loader couldn't even start. `detail` = the error message.
  LOAD_FAILED: "load-failed",
  // The navigation failed (desktop). `detail` = Chromium's error name, `code` its number.
  NAVIGATION: "navigation",
  // The server answered with a 5xx. `code` = the status.
  HTTP: "http",
});

/** The relative URL of the error page for a given failure. */
export function errorPageUrl({ reason, detail, code, url }) {
  const params = new URLSearchParams({ reason });
  if (detail !== undefined) params.set("detail", String(detail));
  if (code !== undefined) params.set("code", String(code));
  if (url !== undefined) params.set("url", String(url));
  return `error.html?${params}`;
}

/** What to tell the user about why they're on the error page. */
export function describeReason(params) {
  const detail = params.get("detail");
  const code = params.get("code");
  switch (params.get("reason")) {
    case ErrorReason.TIMEOUT:
      return `The server took longer than ${detail} seconds to respond.`;
    case ErrorReason.LOAD_FAILED:
      return `The app couldn't start loading the server${detail ? `: ${detail}` : "."}`;
    case ErrorReason.NAVIGATION:
      return `${describeNetError(detail)} (${detail}, code ${code})`;
    case ErrorReason.HTTP:
      return `The server ran into a problem and answered with an error (HTTP ${code}).`;
    default:
      return "The server couldn't be loaded. It might be down, or you might be offline.";
  }
}

// Friendlier text for the Chromium network errors we're most likely to see.
function describeNetError(name) {
  switch (name) {
    case "ERR_INTERNET_DISCONNECTED":
      return "You appear to be offline.";
    case "ERR_NAME_NOT_RESOLVED":
      return "The server's address couldn't be found.";
    case "ERR_CONNECTION_REFUSED":
      return "The server refused the connection. It might be down.";
    case "ERR_CONNECTION_TIMED_OUT":
    case "ERR_TIMED_OUT":
      return "The server took too long to respond.";
    case "ERR_CONNECTION_RESET":
    case "ERR_CONNECTION_CLOSED":
      return "The connection to the server was interrupted.";
    case "ERR_ADDRESS_UNREACHABLE":
      return "The server can't be reached from this network.";
    default:
      if (name?.startsWith("ERR_CERT_") || name?.startsWith("ERR_SSL_")) {
        return "The server's secure connection couldn't be verified.";
      }
      return "The server couldn't be loaded.";
  }
}
