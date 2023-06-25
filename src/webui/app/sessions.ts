import { createCookieSessionStorage } from "@remix-run/node";
import type { AuthTokenExt } from "jupiter-gen";
import { Env } from "jupiter-gen";
import { GLOBAL_PROPERTIES } from "./global-properties-server";

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
      name: GLOBAL_PROPERTIES.sessionCookieName,
      // domain: "http://localhost:10020", // TODO: solve this!
      httpOnly: true,
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: "/",
      sameSite: "lax",
      secure: GLOBAL_PROPERTIES.env === Env.LOCAL ? false : true,
      secrets: [GLOBAL_PROPERTIES.sessionCookieSecret],
    },
  });

export { getSession, commitSession, destroySession };
