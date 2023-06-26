import dotenv from "dotenv";
import type { Env } from "jupiter-gen";

export interface GlobalPropertiesServer {
  env: Env;
  baseName: string;
  description: string;
  hosting: string;
  localWebApiServerUrl: string;
  localWebApiProgressReporterUrl: string;
  globalWebApiServerUrl: string;
  globalWebApiProgressReporterUrl: string;
  sessionCookieSecret: string;
  sessionCookieName: string;
  inboxTasksToAskForGC: number;
  overdueInfoDays: number;
  overdueWarningDays: number;
  overdueDangerDays: number;
}

// @secureFn
function loadGlobalPropertiesOnServer(): GlobalPropertiesServer {
  dotenv.config({ path: `${process.cwd()}/../Config.global` });
  dotenv.config({ path: `${process.cwd()}/Config.project` });

  const globalProperties = {
    env: process.env.ENV as Env,
    baseName: process.env.BASENAME as string,
    description: process.env.DESCRIPTION as string,
    hosting: process.env.HOSTING as string,
    localWebApiServerUrl: process.env.LOCAL_WEBAPI_SERVER_URL as string,
    localWebApiProgressReporterUrl: process.env
      .LOCAL_WEBAPI_PROGRESS_REPORTER_URL as string,
    globalWebApiServerUrl: process.env.GLOBAL_WEBAPI_SERVER_URL as string,
    globalWebApiProgressReporterUrl: process.env
      .GLOBAL_WEBAPI_PROGRESS_REPORTER_URL as string,
    sessionCookieSecret: process.env.SESSION_COOKIE_SECRET as string,
    sessionCookieName: process.env.SESSION_COOKIE_NAME as string,
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