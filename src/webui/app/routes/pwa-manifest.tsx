import { Hosting } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { inferPlatformAndDistribution } from "~/logic/frontdoor.server";

export async function loader({ request }: LoaderArgs) {
  let name = "";
  if (GLOBAL_PROPERTIES.hosting === Hosting.HOSTED_GLOBAL) {
    name = GLOBAL_PROPERTIES.title;
  } else if (GLOBAL_PROPERTIES.hosting === Hosting.SELF_HOSTED) {
    name = `${GLOBAL_PROPERTIES.title} - ${GLOBAL_PROPERTIES.hostingName}`;
  } else {
    name = GLOBAL_PROPERTIES.title;
  }

  const { platform } = inferPlatformAndDistribution(
    request.headers.get("User-Agent")
  );

  const startUrl = new URL(
    "http://example.com" + GLOBAL_PROPERTIES.pwaStartUrl
  );
  startUrl.searchParams.set("clientVersion", GLOBAL_PROPERTIES.version);
  startUrl.searchParams.set("appPlatform", platform);

  return json({
    name: name,
    short_name: name,
    start_url: `${startUrl.pathname}${startUrl.search}`,
    display: "standalone",
    icons: [
      {
        src: "logo.png",
        type: "image/png",
        sizes: "512x512",
      },
    ],
  });
}
