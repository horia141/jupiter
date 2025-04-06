import { AppDistribution, AppPlatform, AppShell } from "@jupiter/webapi-client";
import { z } from "zod";

export interface FrontDoorInfo {
  clientVersion: string;
  appShell: AppShell;
  appPlatform: AppPlatform;
  appDistribution: AppDistribution;
  initialWindowWidth?: number;
}

export const FRONT_DOOR_INFO_SCHEMA = z.object({
  clientVersion: z.string(),
  appShell: z.nativeEnum(AppShell),
  appPlatform: z.nativeEnum(AppPlatform),
  appDistribution: z.nativeEnum(AppDistribution),
  initialWindowWidth: z.optional(
    z.number().or(z.string().transform((s) => parseInt(s))),
  ),
});
