import { AppPlatform, AppShell } from "@jupiter/webapi-client";
import { useMediaQuery, useTheme } from "@mui/material";
import { useContext } from "react";

import { GlobalPropertiesContext } from "~/global-properties-client";

export function useBigScreen(): boolean {
  const globalProperties = useContext(GlobalPropertiesContext);
  const theme = useTheme();
  const mediaQuery = useMediaQuery(theme.breakpoints.up("md"));

  switch (globalProperties.frontDoorInfo.appShell) {
    case AppShell.BROWSER:
      switch (globalProperties.frontDoorInfo.appPlatform) {
        case AppPlatform.DESKTOP_MACOS:
          return mediaQuery;
        case AppPlatform.MOBILE_IOS:
        case AppPlatform.MOBILE_ANDROID:
          return false;
        case AppPlatform.TABLET_IOS:
        case AppPlatform.TABLET_ANDROID:
          return true;
      }
      break;
    case AppShell.DESKTOP_ELECTRON: {
      const mdBreakpointPx = theme.breakpoints.values["md"];

      if (globalProperties.frontDoorInfo.initialWindowWidth !== undefined) {
        if (
          globalProperties.frontDoorInfo.initialWindowWidth > mdBreakpointPx
        ) {
          return true;
        } else {
          return false;
        }
      }

      return true;
    }
    case AppShell.MOBILE_CAPACITOR:
      return false;
    case AppShell.PWA:
      switch (globalProperties.frontDoorInfo.appPlatform) {
        case AppPlatform.DESKTOP_MACOS:
          return mediaQuery;
        case AppPlatform.MOBILE_IOS:
        case AppPlatform.MOBILE_ANDROID:
          return false;
        case AppPlatform.TABLET_IOS:
        case AppPlatform.TABLET_ANDROID:
          return true;
      }
      break;
    default:
      return true;
  }
}
