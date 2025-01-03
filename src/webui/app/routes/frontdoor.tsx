import type { LoaderArgs } from "@remix-run/node";
import { redirect } from "@remix-run/node";
import { parseQuery } from "zodix";
import { getGuestApiClient } from "~/api-clients.server";
import { FRONT_DOOR_INFO_SCHEMA } from "~/logic/frontdoor";
import {
  inferPlatformAndDistributionForMobileShell,
  saveFrontDoorInfo,
} from "~/logic/frontdoor.server";
import { AUTH_TOKEN_NAME } from "~/names";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

import { AppShell } from "@jupiter/webapi-client";

export const handle = {
  displayType: DisplayType.ROOT,
};

// Frontdoor is used by shells as the initial entry point. They can pass
// in shell specific data here, and frondoor stores them in a way that's
// accessible to the rest of the app. Not entering through the frontdoor
// means that the assumptions will be made by the system (ie you're a browser).
export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const params = parseQuery(request, FRONT_DOOR_INFO_SCHEMA);

  if (params.appShell === AppShell.MOBILE_CAPACITOR) {
    const { platform, distribution } =
      inferPlatformAndDistributionForMobileShell(
        request.headers.get("User-Agent")
      );
    params.appPlatform = platform;
    params.appDistribution = distribution;
  }

  if (session.has(AUTH_TOKEN_NAME)) {
    const apiClient = await getGuestApiClient(request);
    const result = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});

    if (result.user || result.workspace) {
      const cookie = await saveFrontDoorInfo(params);
      return redirect("/workspace", {
        headers: {
          "Set-Cookie": cookie,
        },
      });
    }
  }

  return redirect("/login", {
    headers: {
      "Set-Cookie": await saveFrontDoorInfo(params),
    },
  });
}
