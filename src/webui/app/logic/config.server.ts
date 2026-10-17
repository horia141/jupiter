import { AppCore } from "@jupiter/webapi-client";
import {
  GLOBAL_PROPERTIES,
  loadConfigProjectEnv,
  logServiceStartupBanner,
  resolvePublishedUrl,
  resolveWebUiUrl,
} from "@jupiter/core/config-server";
import type { FrontDoorInfo } from "@jupiter/core/frontdoor";

import type { ServicePropertiesClient } from "~/logic/config";

export interface ServicePropertiesServer {
  webApiServerUrl: string;
  webApiProgressReporterUrl: string;
  webApiUrl: string;
  apiUrl: string;
  mcpUrl: string;
  webUiUrl: string;
  publishedUrl: string;
  docsUrl: string;
  pwaStartUrl: string;
  sessionCookieSecure: boolean;
  sessionCookieSecret: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
  googleMapsApiKey: string;
  googleClientId: string;
  googleIosClientId: string;
}

// @secureFn
function loadServicePropertiesOnServer(): ServicePropertiesServer {
  loadConfigProjectEnv(`${process.cwd()}/Config.project`);

  const webApiServerHost = process.env.WEBAPI_SERVER_HOST as string;
  const webApiServerPort = parseInt(
    process.env.WEBAPI_SERVER_PORT as string,
    10,
  );

  const webApiServerUrl = `http://${webApiServerHost}:${webApiServerPort}`;
  const webApiProgressReporterUrl = process.env
    .WEBAPI_PROGRESS_REPORTER_URL as string;

  const serviceProperties = {
    webApiServerUrl: webApiServerUrl,
    webApiProgressReporterUrl: webApiProgressReporterUrl,
    webApiUrl: process.env.WEBAPI_URL as string,
    apiUrl: process.env.API_URL as string,
    mcpUrl: process.env.MCP_URL as string,
    webUiUrl: resolveWebUiUrl(GLOBAL_PROPERTIES),
    publishedUrl: resolvePublishedUrl(GLOBAL_PROPERTIES),
    docsUrl: process.env.DOCS_URL as string,
    pwaStartUrl: process.env.PWA_START_URL as string,
    sessionCookieSecure: process.env.SESSION_COOKIE_SECURE === "true",
    sessionCookieSecret: process.env.SESSION_COOKIE_SECRET as string,
    inboxTasksToAskForGC: parseInt(
      process.env.INBOX_TASKS_TO_ASK_FOR_GC as string,
      10,
    ),
    overdueInfoDays: parseInt(process.env.OVERDUE_INFO_DAYS as string, 10),
    overdueWarningDays: parseInt(
      process.env.OVERDUE_WARNING_DAYS as string,
      10,
    ),
    overdueDangerDays: parseInt(process.env.OVERDUE_DANGER_DAYS as string, 10),
    googleMapsApiKey: process.env.GOOGLE_MAPS_API_KEY ?? "",
    googleClientId: process.env.GOOGLE_CLIENT_ID ?? "",
    googleIosClientId: process.env.GOOGLE_IOS_CLIENT_ID ?? "",
  };

  return serviceProperties;
}

export const SERVICE_PROPERTIES = loadServicePropertiesOnServer();

logServiceStartupBanner("webui");

export function serverToClientServiceProperties(
  servicePropertiesServer: ServicePropertiesServer,
  frontDoorInfo: FrontDoorInfo,
): ServicePropertiesClient {
  return {
    appCore: AppCore.WEBUI,
    frontDoorInfo: frontDoorInfo,
    webApiProgressReporterUrl:
      servicePropertiesServer.webApiProgressReporterUrl,
    webApiUrl: servicePropertiesServer.webApiUrl,
    apiUrl: servicePropertiesServer.apiUrl,
    mcpUrl: servicePropertiesServer.mcpUrl,
    webUiUrl: servicePropertiesServer.webUiUrl,
    publishedUrl: servicePropertiesServer.publishedUrl,
    docsUrl: servicePropertiesServer.docsUrl,
    inboxTasksToAskForGC: servicePropertiesServer.inboxTasksToAskForGC,
    overdueInfoDays: servicePropertiesServer.overdueInfoDays,
    overdueWarningDays: servicePropertiesServer.overdueWarningDays,
    overdueDangerDays: servicePropertiesServer.overdueDangerDays,
    googleMapsApiKey: publicGoogleMapsApiKey(
      servicePropertiesServer.googleMapsApiKey,
    ),
    nativeSignIn: {
      googleWebClientId: servicePropertiesServer.googleClientId,
      googleIosClientId: servicePropertiesServer.googleIosClientId,
    },
  };
}

function publicGoogleMapsApiKey(raw: string): string | null {
  const trimmed = raw.trim();
  if (trimmed === "" || trimmed === "FAKEFAKE") {
    return null;
  }
  return trimmed;
}
