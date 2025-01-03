import { AppDistribution, AppPlatform, AppShell } from "@jupiter/webapi-client";
import { z } from "zod";

export interface FrontDoorInfo {
  appShell: AppShell;
  appPlatform: AppPlatform;
  appDistribution: AppDistribution;
  initialWindowWidth?: number;
}

export const FRONT_DOOR_INFO_SCHEMA = z.object({
  appShell: z.nativeEnum(AppShell),
  appPlatform: z.nativeEnum(AppPlatform),
  appDistribution: z.nativeEnum(AppDistribution).optional().transform((v) => v ?? AppDistribution.WEB),
  initialWindowWidth: z.optional(
    z.number().or(z.string().transform((s) => parseInt(s)))
  ),
});
