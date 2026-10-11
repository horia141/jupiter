import { AppDistribution, AppPlatform, AppShell } from "@jupiter/webapi-client";
import { describe, expect, it } from "vitest";

import {
  FRONT_DOOR_INFO_SCHEMA,
  hasShellFeature,
  ShellFeature,
} from "#/core/frontdoor";

const BASE = {
  clientVersion: "1.3.3",
  appShell: AppShell.MOBILE_CAPACITOR,
  appPlatform: AppPlatform.MOBILE_IOS,
  appDistribution: AppDistribution.APP_STORE,
};

describe("FRONT_DOOR_INFO_SCHEMA", () => {
  it("reads shell features from the URL's comma-separated list", () => {
    const info = FRONT_DOOR_INFO_SCHEMA.parse({
      ...BASE,
      shellFeatures: "local-picker,external-browser",
    });
    expect(info.shellFeatures).toEqual(["local-picker", "external-browser"]);
  });

  it("reads shell features back from the cookie's array", () => {
    const info = FRONT_DOOR_INFO_SCHEMA.parse({
      ...BASE,
      shellFeatures: ["local-picker"],
    });
    expect(info.shellFeatures).toEqual(["local-picker"]);
  });

  it("accepts shells that list no features", () => {
    expect(FRONT_DOOR_INFO_SCHEMA.parse(BASE).shellFeatures).toBeUndefined();
    expect(
      FRONT_DOOR_INFO_SCHEMA.parse({ ...BASE, shellFeatures: "" })
        .shellFeatures,
    ).toEqual([]);
  });
});

describe("hasShellFeature", () => {
  it("is true only for listed features", () => {
    const info = FRONT_DOOR_INFO_SCHEMA.parse({
      ...BASE,
      shellFeatures: "local-picker,some-future-feature",
    });
    expect(hasShellFeature(info, ShellFeature.LOCAL_PICKER)).toBe(true);
    expect(hasShellFeature(info, ShellFeature.EXTERNAL_BROWSER)).toBe(false);
  });

  it("is false for an older shell that lists nothing", () => {
    const info = FRONT_DOOR_INFO_SCHEMA.parse(BASE);
    expect(hasShellFeature(info, ShellFeature.LOCAL_PICKER)).toBe(false);
  });
});
