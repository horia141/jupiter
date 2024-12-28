import { AppPlatform, AppShell } from "@jupiter/webapi-client";
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
    return {
      appShell: AppShell.BROWSER,
      appPlatform: inferPlatform(userAgent),
      initialWindowWidth: undefined,
    };
  }

  const frontDoorInfoRaw = await frontDoorCookie.parse(cookie);

  const maybeFrontDoor = FRONT_DOOR_INFO_SCHEMA.safeParse(frontDoorInfoRaw);

  if (!maybeFrontDoor.success) {
    return {
      appShell: AppShell.BROWSER,
      appPlatform: inferPlatform(userAgent),
      initialWindowWidth: undefined,
    };
  }

  return maybeFrontDoor.data;
}

export function inferPlatform(userAgent: string | null): AppPlatform {
  if (userAgent === null) {
    return AppPlatform.DESKTOP;
  }

  const ua = uap.UAParser(userAgent);

  if (ua.device.type === "mobile" && ua.os.name === "iOS") {
    return AppPlatform.MOBILE_IOS;
  } else if (ua.device.type === "mobile" && ua.os.name === "Android") {
    return AppPlatform.MOBILE_ANDROID;
  } else if (ua.device.type === "tablet" && ua.os.name === "iOS") {
    return AppPlatform.TABLET_IOS;
  } else if (ua.device.type === "tablet" && ua.os.name === "Android") {
    return AppPlatform.TABLET_ANDROID;
  } else {
    return AppPlatform.DESKTOP;
  }
}

export function inferPlatformForMobileShell(userAgent: string | null): AppPlatform {
  if (userAgent === null) {
    return AppPlatform.TABLET_IOS;
  }

  const ua = uap.UAParser(userAgent);

  if (ua.device.type === "mobile" && ua.os.name === "iOS") {
    return AppPlatform.MOBILE_IOS;
  } else if (ua.device.type === "mobile" && ua.os.name === "Android") {
    return AppPlatform.MOBILE_ANDROID;
  } else if (ua.device.type === "tablet" && ua.os.name === "iOS") {
    return AppPlatform.TABLET_IOS;
  } else if (ua.device.type === "tablet" && ua.os.name === "Android") {
    return AppPlatform.TABLET_ANDROID;
  } else {
    return AppPlatform.TABLET_IOS;
  }
}
