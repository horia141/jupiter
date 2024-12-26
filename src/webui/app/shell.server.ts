import { AppShell } from "@jupiter/webapi-client";
import { createCookie } from "@remix-run/node";
import { APPSHELL_COOKIE_NAME } from "./names";

export const appShellCookie = createCookie(APPSHELL_COOKIE_NAME, {
  maxAge: 60 * 60 * 24 * 365 * 20,
  path: "/",
  sameSite: "strict",
});

export async function saveAppShell(appShell: AppShell) {
  return await appShellCookie.serialize(appShell);
}

export async function loadAppShell(cookie: string | null): Promise<AppShell> {
  if (cookie === null) {
    return AppShell.BROWSER;
  }

  const appShellRaw = await appShellCookie.parse(cookie);

  // If appShellRaw is null, undefined or a non-string, return the default value
  if (typeof appShellRaw !== "string") {
    return AppShell.BROWSER;
  }

  switch (appShellRaw) {
    case AppShell.BROWSER:
    case AppShell.DESKTOP_ELECTRON:
    case AppShell.MOBILE_CAPACITOR:
    case AppShell.MOBILE_PWA:
      return appShellRaw as AppShell;
    default:
      return AppShell.BROWSER;
  }
}
