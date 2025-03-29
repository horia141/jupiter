import { SplashScreen } from "@capacitor/splash-screen";
import { getWebUiUrl } from "./config";

document.addEventListener("DOMContentLoaded", async () => {
  await SplashScreen.hide();
  const webUiUrl = await getWebUiUrl();

  try {
    await loadURLWithTimeout(webUiUrl.toString());
  } catch (err) {
    console.error(`Error loading URL: ${err.message}`);
    window.location.href = "/error.html";
  }
});

function loadURLWithTimeout(url, timeout = 10000) {
  return new Promise((resolve, reject) => {
    let isTimeout = false;

    const timeoutId = setTimeout(() => {
      isTimeout = true;
      window.removeEventListener("load", handleLoad);
      window.removeEventListener("error", handleError);
      reject(new Error(`Loading URL timed out after ${timeout} ms`));
    }, timeout);

    const handleLoad = () => {
      if (!isTimeout) {
        clearTimeout(timeoutId);
        window.removeEventListener("load", handleLoad);
        window.removeEventListener("error", handleError);
        resolve();
      }
    };

    const handleError = () => {
      if (!isTimeout) {
        clearTimeout(timeoutId);
        window.removeEventListener("load", handleLoad);
        window.removeEventListener("error", handleError);
        reject(new Error("Failed to load URL"));
      }
    };

    setTimeout(() => {
      window.location.href = url;
      window.addEventListener("load", handleLoad);
      window.addEventListener("error", handleError);
    }, 100);
  });
}
