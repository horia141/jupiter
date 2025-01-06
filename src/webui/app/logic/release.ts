import { AppDistribution, AppDistributionState } from "@jupiter/webapi-client";
import { z } from "zod";

export const RELEASE_MANIFEST_SCHEMA = z.record(
  z.nativeEnum(AppDistribution),
  z.nativeEnum(AppDistributionState)
);

export type ReleaseManifest = Record<AppDistribution, AppDistributionState>;

export interface ReleaseManifestResult {
  latestServerVersion: string;
  manifest: ReleaseManifest;
}
