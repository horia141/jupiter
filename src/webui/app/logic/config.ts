import {
  AppCore,
  AppDistribution,
  AppPlatform,
  AppShell,
} from "@jupiter/webapi-client";
import { createContext, useContext } from "react";
import type { FrontDoorInfo } from "@jupiter/core/frontdoor";

export interface ServicePropertiesClient {
  appCore: AppCore;
  frontDoorInfo: FrontDoorInfo;
  webApiProgressReporterUrl: string;
  webApiUrl: string;
  apiUrl: string;
  mcpUrl: string;
  webUiUrl: string;
  publishedUrl: string;
  docsUrl: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
  googleMapsApiKey: string | null;
  nativeSignIn: NativeSignInConfig;
}

/** Public client ids the native Google SDK needs to start. */
export interface NativeSignInConfig {
  googleWebClientId: string;
  googleIosClientId: string;
}

export const ServicePropertiesContext = createContext<ServicePropertiesClient>({
  appCore: AppCore.WEBUI,
  frontDoorInfo: {
    clientVersion: "FAKE-FAKE",
    appShell: AppShell.BROWSER,
    appPlatform: AppPlatform.DESKTOP_MACOS,
    appDistribution: AppDistribution.WEB,
    initialWindowWidth: undefined,
  },
  webApiProgressReporterUrl: "FAKE-FAKE",
  webApiUrl: "FAKE-FAKE",
  apiUrl: "FAKE-FAKE",
  mcpUrl: "FAKE-FAKE",
  webUiUrl: "FAKE-FAKE",
  publishedUrl: "FAKE-FAKE",
  docsUrl: "FAKE-FAKE",
  inboxTasksToAskForGC: 20,
  overdueInfoDays: 1,
  overdueWarningDays: 2,
  overdueDangerDays: 3,
  googleMapsApiKey: null,
  nativeSignIn: { googleWebClientId: "", googleIosClientId: "" },
});

export function useServiceProperties(): ServicePropertiesClient {
  return useContext(ServicePropertiesContext);
}
