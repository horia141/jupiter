import { AppShell } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { redirect } from "@remix-run/node";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getGuestApiClient } from "~/api-clients.server";
import { AUTH_TOKEN_NAME } from "~/names";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { saveAppShell } from "~/shell.server";

const ParamsSchema = {
  appShell: z.nativeEnum(AppShell),
};

export const handle = {
  displayType: DisplayType.ROOT,
};

// Frontdoor is used by shells as the initial entry point. They can pass
// in shell specific data here, and frondoor stores them in a way that's
// accessible to the rest of the app. Not entering through the frontdoor
// means that the assumptions will be made by the system (ie you're a browser).
export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const params = parseQuery(request, ParamsSchema);

  if (session.has(AUTH_TOKEN_NAME)) {
    const apiClient = await getGuestApiClient(request);
    const result = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});

    if (result.user || result.workspace) {
      return redirect("/workspace", {
        headers: {
          "Set-Cookie": await saveAppShell(params.appShell),
        },
      });
    }
  }

  return redirect("/login", {
    headers: {
      "Set-Cookie": await saveAppShell(params.appShell),
    },
  });
}
