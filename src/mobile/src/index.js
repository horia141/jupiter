import { SplashScreen } from "@capacitor/splash-screen";
import { getWebUiUrl } from "./config";

document.addEventListener('DOMContentLoaded', async () => {
    await SplashScreen.hide();
    const webUiUrl = await getWebUiUrl();
    window.location.href = webUiUrl.toString();
});
