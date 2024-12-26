import { AppCore, AppShell, Env, Hosting } from "@jupiter/webapi-client";
import { createContext } from "react";
import type { GlobalPropertiesServer } from "./global-properties-server";

export interface GlobalPropertiesClient {
  env: Env;
  hosting: Hosting;
  appCore: AppCore;
  appShell: AppShell;
  baseName: string;
  title: string;
  description: string;
  webApiProgressReporterUrl: string;
  docsUrl: string;
  communityUrl: string;
  termsOfServiceUrl: string;
  privacyPolicyUrl: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
}

export const GlobalPropertiesContext = createContext<GlobalPropertiesClient>({
  env: Env.LOCAL,
  hosting: Hosting.LOCAL,
  appCore: AppCore.WEBUI,
  appShell: AppShell.BROWSER,
  baseName: "FAKE-FAKE",
  title: "FAKE-FAKE",
  description: "FAKE-FAKE",
  webApiProgressReporterUrl: "FAKE-FAKE",
  docsUrl: "FAKE-FAKE",
  communityUrl: "FAKE-FAKE",
  termsOfServiceUrl: "FAKE-FAKE",
  privacyPolicyUrl: "FAKE-FAKE",
  inboxTasksToAskForGC: 20,
  overdueInfoDays: 1,
  overdueWarningDays: 2,
  overdueDangerDays: 3,
});

export function serverToClientGlobalProperties(
  globalPropertiesServer: GlobalPropertiesServer,
  appShell: AppShell
): GlobalPropertiesClient {
  return {
    env: globalPropertiesServer.env,
    hosting: globalPropertiesServer.hosting,
    appCore: AppCore.WEBUI,
    appShell: appShell,
    baseName: globalPropertiesServer.baseName,
    title: globalPropertiesServer.title,
    description: globalPropertiesServer.description,
    webApiProgressReporterUrl:
      globalPropertiesServer.hosting === Hosting.LOCAL
        ? globalPropertiesServer.localWebApiProgressReporterUrl
        : globalPropertiesServer.hostedGlobalWebApiProgressReporterUrl,
    docsUrl: globalPropertiesServer.docsUrl,
    communityUrl: globalPropertiesServer.communityUrl,
    termsOfServiceUrl: globalPropertiesServer.termsOfServiceUrl,
    privacyPolicyUrl: globalPropertiesServer.privacyPolicyUrl,
    inboxTasksToAskForGC: globalPropertiesServer.inboxTasksToAskForGC,
    overdueInfoDays: globalPropertiesServer.overdueInfoDays,
    overdueWarningDays: globalPropertiesServer.overdueWarningDays,
    overdueDangerDays: globalPropertiesServer.overdueDangerDays,
  };
}
