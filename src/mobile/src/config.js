import { Capacitor } from '@capacitor/core';
import { Device } from '@capacitor/device';

import { AppDistribution } from '../../../gen/ts/webapi-client/gen/models/AppDistribution';
import { AppPlatform } from '../../../gen/ts/webapi-client/gen/models/AppPlatform';

export async function getWebUiUrl() {
    const asUrl = new URL(window.WEBUI_URL);

    const deviceType = await checkDeviceType();
    
    asUrl.searchParams.set("clientVersion", window.CLIENT_VERSION);
    
    if (Capacitor.getPlatform() === "ios") {
        if (deviceType === 'tablet') {
            asUrl.searchParams.set("appPlatform", AppPlatform.TABLET_IOS);
        } else {
            asUrl.searchParams.set("appPlatform", AppPlatform.MOBILE_IOS);
        }
        asUrl.searchParams.set("appDistribution", AppDistribution.APP_STORE);
    } else if (Capacitor.getPlatform() === "android") {
        if (deviceType === 'tablet') {
            asUrl.searchParams.set("appPlatform", AppPlatform.TABLET_ANDROID);
        } else {
            asUrl.searchParams.set("appPlatform", AppPlatform.MOBILE_ANDROID);
        }
        asUrl.searchParams.set("appDistribution", AppDistribution.GOOGLE_PLAY_STORE);
    }
    
    return asUrl;
}


async function checkDeviceType() {
    const info = await Device.getInfo();

    if (info.platform === 'ios') {
      // On iOS, check the model or other properties
      return info.model?.includes('iPad') ? 'tablet' : 'phone';
    } else if (info.platform === 'android') {
      // On Android, use heuristic methods
      const isTablet = await isAndroidTablet(info);
      return isTablet ? 'tablet' : 'phone';
    } else {
      return 'unknown'; // Web or other platforms
    }
  }
  
  async function isAndroidTablet(info) {
    const width = window.screen.width;
    const height = window.screen.height;
    const dpi = window.devicePixelRatio;
  
    const screenSizeInInches = Math.sqrt(
      (width / dpi) ** 2 + (height / dpi) ** 2
    );
  
    return screenSizeInInches >= 7; // Heuristic: 7 inches or larger is considered a tablet
  }