import { json } from "@remix-run/node";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { RELEASE_MANIFEST_SCHEMA } from "~/logic/release";

export async function loader() {
  const manifestFetch = await fetch(
    GLOBAL_PROPERTIES.appsStorageUrl +
      "/v" +
      GLOBAL_PROPERTIES.version +
      "/release-manifest.json",
    { cache: "no-store" }
  );
  const manifestRaw = await manifestFetch.json();
  const manifest = RELEASE_MANIFEST_SCHEMA.parse(manifestRaw);
  return json({
    latestServerVersion: GLOBAL_PROPERTIES.version,
    manifest: manifest,
  });
}