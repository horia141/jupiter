import { SplashScreen } from "@capacitor/splash-screen";
import { getWebUiUrl } from "./config";

document.addEventListener('DOMContentLoaded', async () => {
    await SplashScreen.hide();

    const button = document.getElementById("retry");
    button.addEventListener("click", retry);
});

export async function retry(event) {
    event.preventDefault();
    const webUiUrl = await getWebUiUrl();
    window.location.href = webUiUrl.toString();
}
