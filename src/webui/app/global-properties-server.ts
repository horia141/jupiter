import type { Env, Hosting } from "@jupiter/webapi-client";
import dotenv from "dotenv";

export interface GlobalPropertiesServer {
  env: Env;
  hosting: Hosting;
  baseName: string;
  version: string;
  title: string;
  description: string;
  localWebApiServerUrl: string;
  localWebApiProgressReporterUrl: string;
  hostedGlobalWebApiServerUrl: string;
  hostedGlobalWebApiProgressReporterUrl: string;
  docsUrl: string;
  communityUrl: string;
  appsStorageUrl: string;
  macStoreUrl: string;
  appStoreUrl: string;
  googlePlayStoreUrl: string;
  termsOfServiceUrl: string;
  privacyPolicyUrl: string;
  sessionCookieSecret: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
}

// @secureFn
function loadGlobalPropertiesOnServer(): GlobalPropertiesServer {
  dotenv.config({ path: `${process.cwd()}/../Config.global` });
  dotenv.config({ path: `${process.cwd()}/Config.project` });

  const hostedGlobalWebApiServerHost = process.env
    .HOSTED_GLOBAL_WEBAPI_SERVER_HOST as string;
  const hostedGlobalWebApiServerPort = parseInt(
    process.env.HOSTED_GLOBAL_WEBAPI_SERVER_PORT as string,
    10
  );

  const hostedGlobalWebApiServerUrl = `http://${hostedGlobalWebApiServerHost}:${hostedGlobalWebApiServerPort}`;
  const hostedGlobalWebApiProgressReporterUrl = `wss://${hostedGlobalWebApiServerHost}:${hostedGlobalWebApiServerPort}/progress-reporter`;

  const globalProperties = {
    env: process.env.ENV as Env,
    hosting: process.env.HOSTING as Hosting,
    baseName: process.env.BASENAME as string,
    version: process.env.VERSION as string,
    title: process.env.TITLE as string,
    description: process.env.DESCRIPTION as string,
    localWebApiServerUrl: process.env.LOCAL_WEBAPI_SERVER_URL as string,
    localWebApiProgressReporterUrl: process.env
      .LOCAL_WEBAPI_PROGRESS_REPORTER_URL as string,
    hostedGlobalWebApiServerUrl: hostedGlobalWebApiServerUrl,
    hostedGlobalWebApiProgressReporterUrl:
      hostedGlobalWebApiProgressReporterUrl,
    docsUrl: process.env.DOCS_URL as string,
    communityUrl: process.env.COMMUNITY_URL as string,
    appsStorageUrl: process.env.APPS_STORAGE_URL as string,
    macStoreUrl: process.env.MAC_STORE_URL as string,
    appStoreUrl: process.env.APP_STORE_URL as string,
    googlePlayStoreUrl: process.env.GOOGLE_PLAY_STORE_URL as string,
    termsOfServiceUrl: process.env.TERMS_OF_SERVICE_URL as string,
    privacyPolicyUrl: process.env.PRIVACY_POLICY_URL as string,
    sessionCookieSecret: process.env.SESSION_COOKIE_SECRET as string,
    inboxTasksToAskForGC: parseInt(
      process.env.INBOX_TASKS_TO_ASK_FOR_GC as string,
      10
    ),
    overdueInfoDays: parseInt(process.env.OVERDUE_INFO_DAYS as string, 10),
    overdueWarningDays: parseInt(
      process.env.OVERDUE_WARNING_DAYS as string,
      10
    ),
    overdueDangerDays: parseInt(process.env.OVERDUE_DANGER_DAYS as string, 10),
  };

  return globalProperties;
}

export const GLOBAL_PROPERTIES = loadGlobalPropertiesOnServer();
