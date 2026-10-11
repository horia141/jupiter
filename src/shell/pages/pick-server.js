import * as adapter from "#adapter";

import { isSameOrigin } from "./shell.js";

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("pick-server-form");
  const field = document.getElementById("server-url-field");
  const input = document.getElementById("server-url");
  const error = document.getElementById("server-url-error");
  const connect = document.getElementById("connect");
  const useGlobal = document.getElementById("use-global");
  const goBack = document.getElementById("go-back");

  await adapter.init();

  const { serverUrl, hostedGlobalUrl } = await adapter.getServerInfo();
  if (!isSameOrigin(serverUrl, hostedGlobalUrl)) {
    input.value = serverUrl;
  }

  function setBusy(busy) {
    for (const el of [input, connect, useGlobal, goBack]) {
      el.disabled = busy;
    }
    connect.textContent = busy ? "Checking…" : "Pick Server";
  }

  function setError(message) {
    error.textContent = message ?? "";
    field.classList.toggle("invalid", Boolean(message));
    input.setAttribute("aria-invalid", message ? "true" : "false");
  }

  input.addEventListener("input", () => setError(null));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setError(null);
    setBusy(true);

    // On success the adapter saves the server and navigates to it.
    const res = await adapter.pickServer(input.value);
    if (res.result === "error") {
      setError(res.errorMsg);
      setBusy(false);
    }
  });

  useGlobal.addEventListener("click", () => {
    input.value = hostedGlobalUrl;
    setError(null);
    input.focus();
  });

  goBack.addEventListener("click", () => {
    window.location.href = "index.html";
  });
});
