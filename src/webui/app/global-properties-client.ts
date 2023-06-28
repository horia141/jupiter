import { Env } from "jupiter-gen";
import { createContext } from "react";
import type { GlobalPropertiesServer } from "./global-properties-server";

export interface GlobalPropertiesClient {
  env: Env;
  baseName: string;
  description: string;
  hostedGlobalWebApiServerHost: string;
  hostedGlobalWebApiServerPort: number;
  webApiProgressReporterUrl: string;
  docsUrl: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
}

export const GlobalPropertiesContext = createContext<GlobalPropertiesClient>({
  env: Env.LOCAL,
  baseName: "FAKE-FAKE",
  description: "FAKE-FAKE",
  hostedGlobalWebApiServerHost: "FAKE-FAKE",
  hostedGlobalWebApiServerPort: -10,
  webApiProgressReporterUrl: "FAKE-FAKE",
  docsUrl: "FAKE-FAKE",
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
    baseName: globalPropertiesServer.baseName,
    description: globalPropertiesServer.description,
    hostedGlobalWebApiServerHost:
      globalPropertiesServer.hostedGlobalWebApiServerHost,
    hostedGlobalWebApiServerPort:
      globalPropertiesServer.hostedGlobalWebApiServerPort,
    webApiProgressReporterUrl:
      globalPropertiesServer.hosting === "LOCAL"
        ? globalPropertiesServer.localWebApiProgressReporterUrl
        : globalPropertiesServer.hostedGlobalWebApiProgressReporterUrl,
    docsUrl: globalPropertiesServer.docsUrl,
    inboxTasksToAskForGC: globalPropertiesServer.inboxTasksToAskForGC,
    overdueInfoDays: globalPropertiesServer.overdueInfoDays,
    overdueWarningDays: globalPropertiesServer.overdueWarningDays,
    overdueDangerDays: globalPropertiesServer.overdueDangerDays,
  };
}
