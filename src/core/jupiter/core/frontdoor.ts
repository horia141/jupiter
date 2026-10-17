import { AppDistribution, AppPlatform, AppShell } from "@jupiter/webapi-client";
import { z } from "zod";

/**
 * Things an app shell can do, which it lists in the frontdoor URL. The webui
 * only relies on one when the shell says it has it, so older app builds keep
 * working against a newer server.
 */
export enum ShellFeature {
  // The shell has its own server picker the webui can hand over to.
  LOCAL_PICKER = "local-picker",
  // The shell can open links in the system browser (@capacitor/browser).
  EXTERNAL_BROWSER = "external-browser",
  // The shell has the native Google/Apple sign-in SDKs (@capgo/capacitor-social-login),
  // since the redirect flow can't hand the session back from the system browser.
  NATIVE_SIGN_IN = "native-sign-in",
}

export interface FrontDoorInfo {
  clientVersion: string;
  appShell: AppShell;
  appPlatform: AppPlatform;
  appDistribution: AppDistribution;
  initialWindowWidth?: number;
  shellFeatures?: string[];
}

export const FRONT_DOOR_INFO_SCHEMA = z.object({
  clientVersion: z.string(),
  appShell: z.nativeEnum(AppShell),
  appPlatform: z.nativeEnum(AppPlatform),
  appDistribution: z.nativeEnum(AppDistribution),
  initialWindowWidth: z.optional(
    z.number().or(z.string().transform((s) => parseInt(s))),
  ),
  // A comma-separated list in the URL, an array once saved in the cookie.
  shellFeatures: z.optional(
    z
      .array(z.string())
      .or(z.string().transform((s) => s.split(",").filter((f) => f !== ""))),
  ),
});

export function hasShellFeature(
  frontDoor: FrontDoorInfo,
  feature: ShellFeature,
): boolean {
  return frontDoor.shellFeatures?.includes(feature) ?? false;
}
