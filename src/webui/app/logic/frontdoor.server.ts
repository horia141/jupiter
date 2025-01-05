import { AppDistribution, AppPlatform, AppShell } from "@jupiter/webapi-client";
import { createCookie } from "@remix-run/node";
import uap from "ua-parser-js";
import { FRONTDOOR_COOKIE_NAME } from "../names";
import type { FrontDoorInfo } from "./frontdoor";
import { FRONT_DOOR_INFO_SCHEMA } from "./frontdoor";

export const frontDoorCookie = createCookie(FRONTDOOR_COOKIE_NAME, {
  maxAge: 60 * 60 * 24 * 365 * 20,
  path: "/",
  sameSite: "strict",
});

export async function saveFrontDoorInfo(info: FrontDoorInfo) {
  return await frontDoorCookie.serialize(info);
}

export async function loadFrontDoorInfo(
  cookie: string | null,
  userAgent: string | null
): Promise<FrontDoorInfo> {
  if (cookie === null) {
    const { platform, distribution } = inferPlatformAndDistribution(userAgent);
    return {
      appShell: AppShell.BROWSER,
      appPlatform: platform,
      appDistribution: distribution,
      initialWindowWidth: undefined,
    };
  }

  const frontDoorInfoRaw = await frontDoorCookie.parse(cookie);

  const maybeFrontDoor = FRONT_DOOR_INFO_SCHEMA.safeParse(frontDoorInfoRaw);

  if (!maybeFrontDoor.success) {
    const { platform, distribution } = inferPlatformAndDistribution(userAgent);
    return {
      appShell: AppShell.BROWSER,
      appPlatform: platform,
      appDistribution: distribution,
      initialWindowWidth: undefined,
    };
  }

  return maybeFrontDoor.data;
}

export function inferPlatformAndDistribution(userAgent: string | null): {
  platform: AppPlatform;
  distribution: AppDistribution;
} {
  if (userAgent === null) {
    return { platform: AppPlatform.DESKTOP, distribution: AppDistribution.WEB };
  }

  const ua = uap.UAParser(userAgent);

  if (ua.device.type === "mobile" && ua.os.name === "iOS") {
    return {
      platform: AppPlatform.MOBILE_IOS,
      distribution: AppDistribution.APP_STORE,
    };
  } else if (ua.device.type === "mobile" && ua.os.name === "Android") {
    return {
      platform: AppPlatform.MOBILE_ANDROID,
      distribution: AppDistribution.GOOGLE_PLAY_STORE,
    };
  } else if (ua.device.type === "tablet" && ua.os.name === "iOS") {
    return {
      platform: AppPlatform.TABLET_IOS,
      distribution: AppDistribution.APP_STORE,
    };
  } else if (ua.device.type === "tablet" && ua.os.name === "Android") {
    return {
      platform: AppPlatform.TABLET_ANDROID,
      distribution: AppDistribution.GOOGLE_PLAY_STORE,
    };
  } else {
    return { platform: AppPlatform.DESKTOP, distribution: AppDistribution.WEB };
  }
}
