import * as adapter from "#adapter";

import { ErrorReason, errorPageUrl } from "../lib/errors.js";
import { SHELL_CONFIG } from "./shell.js";

document.addEventListener("DOMContentLoaded", async () => {
  let webUiUrl;
  try {
    await adapter.init();
    const hostedGlobal =
      new URLSearchParams(window.location.search).get("hostedGlobal") ===
      "true";
    webUiUrl = await adapter.getWebUiUrl({ hostedGlobal });
    document.getElementById("server").textContent = new URL(webUiUrl).origin;
  } catch (err) {
    console.error(`Error preparing to load: ${err.message}`);
    window.location.replace(
      errorPageUrl({ reason: ErrorReason.LOAD_FAILED, detail: err.message }),
    );
    return;
  }

  // Leaving for the server unloads this page and with it the timer, so the
  // timer only fires if the server never answers. Connection failures and
  // server errors are caught by the native layer, which shows the error page.
  window.location.href = webUiUrl;
  setTimeout(() => {
    window.location.replace(
      errorPageUrl({
        reason: ErrorReason.TIMEOUT,
        detail: Math.round(SHELL_CONFIG.loadTimeoutMs / 1000),
        url: webUiUrl,
      }),
    );
  }, SHELL_CONFIG.loadTimeoutMs);
});
