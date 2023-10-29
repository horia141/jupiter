import { Env, Hosting } from "jupiter-gen";
import { createContext } from "react";
import type { GlobalPropertiesServer } from "./global-properties-server";

export interface GlobalPropertiesClient {
  env: Env;
  hosting: Hosting;
  baseName: string;
  title: string;
  description: string;
  webApiProgressReporterUrl: string;
  docsUrl: string;
  scoreActionCookieName: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
}

export const GlobalPropertiesContext = createContext<GlobalPropertiesClient>({
  env: Env.LOCAL,
  hosting: Hosting.LOCAL,
  baseName: "FAKE-FAKE",
  title: "FAKE-FAKE",
  description: "FAKE-FAKE",
  webApiProgressReporterUrl: "FAKE-FAKE",
  docsUrl: "FAKE-FAKE",
  scoreActionCookieName: "FAKE-FAKE",
  inboxTasksToAskForGC: 20,
  overdueInfoDays: 1,
  overdueWarningDays: 2,
  overdueDangerDays: 3,
});

export function serverToClientGlobalProperties(
  globalPropertiesServer: GlobalPropertiesServer
): GlobalPropertiesClient {
  return {
    env: globalPropertiesServer.env,
    hosting: globalPropertiesServer.hosting,
    baseName: globalPropertiesServer.baseName,
    title: globalPropertiesServer.title,
    description: globalPropertiesServer.description,
    webApiProgressReporterUrl:
      globalPropertiesServer.hosting === Hosting.LOCAL
        ? globalPropertiesServer.localWebApiProgressReporterUrl
        : globalPropertiesServer.hostedGlobalWebApiProgressReporterUrl,
    docsUrl: globalPropertiesServer.docsUrl,
    scoreActionCookieName: globalPropertiesServer.scoreActionCookieName,
    inboxTasksToAskForGC: globalPropertiesServer.inboxTasksToAskForGC,
    overdueInfoDays: globalPropertiesServer.overdueInfoDays,
    overdueWarningDays: globalPropertiesServer.overdueWarningDays,
    overdueDangerDays: globalPropertiesServer.overdueDangerDays,
  };
}
