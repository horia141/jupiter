import type { AuthTokenExt } from "@jupiter/webapi-client";
import { createCookieSessionStorage } from "@remix-run/node";

import { GLOBAL_PROPERTIES } from "./global-properties-server";
import { SESSION_COOKIE_NAME } from "./names";

export class SessionInfoNotFoundError extends Error {
  constructor() {
    super("Session info not found");
  }
}

export interface SessionInfo {
  authTokenExt: AuthTokenExt;
}

export interface SessionFlashInfo {
  error: string;
}

const { getSession, commitSession, destroySession } =
  createCookieSessionStorage({
    cookie: {
      name: SESSION_COOKIE_NAME,
      httpOnly: true,
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: "/",
      sameSite: "lax", // Not strict because of https://github.com/oauth2-proxy/oauth2-proxy/issues/830
      secure: GLOBAL_PROPERTIES.sessionCookieSecure,
      secrets: [GLOBAL_PROPERTIES.sessionCookieSecret],
    },
  });

export { getSession, commitSession, destroySession };
