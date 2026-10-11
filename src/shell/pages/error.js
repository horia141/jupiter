import * as adapter from "#adapter";

import { describeReason } from "../lib/errors.js";
import { isSameOrigin } from "./shell.js";

// We get here from the loader, from the native layer when a navigation fails
// or the server answers with a 5xx, or from Capacitor's errorPath with no
// details at all. So besides saying why we're here, we check the server
// ourselves to say what is actually wrong.
document.addEventListener("DOMContentLoaded", async () => {
  const message = document.getElementById("message");
  const server = document.getElementById("server");
  const problem = document.getElementById("problem");
  const useGlobal = document.getElementById("use-global");
  const exit = document.getElementById("exit");

  document.getElementById("retry").addEventListener("click", () => {
    window.location.href = "index.html";
  });
  document.getElementById("change-server").addEventListener("click", () => {
    window.location.href = "pick-server.html";
  });
  useGlobal.addEventListener("click", () => {
    window.location.href = "index.html?hostedGlobal=true";
  });
  exit.hidden = !adapter.canExit;
  exit.addEventListener("click", () => adapter.exit());

  await adapter.init();

  const params = new URLSearchParams(window.location.search);
  message.textContent = describeReason(params);

  const { serverUrl, hostedGlobalUrl } = await adapter.getServerInfo();
  const failedOrigin = new URL(params.get("url") ?? serverUrl).origin;
  const isGlobal = isSameOrigin(failedOrigin, hostedGlobalUrl);
  server.textContent = isGlobal ? `${failedOrigin} (official)` : failedOrigin;
  useGlobal.hidden = isGlobal;

  const res = await adapter.checkServer(failedOrigin);
  problem.classList.remove("pending");
  if (res.result === "error") {
    problem.classList.add("problem");
    problem.textContent = res.errorMsg;
  } else {
    problem.textContent =
      "None found now. The server responds and is compatible, so this may have been temporary. Try again.";
  }
});
