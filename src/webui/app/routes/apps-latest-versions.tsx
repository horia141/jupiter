import { AppDistribution } from "@jupiter/webapi-client";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { redirect } from "@remix-run/node";
import { z } from "zod";
import { parseQuery } from "zodix";

import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { VERSION_HEADER } from "~/names";

const QuerySchema = z.object({
  distribution: z.nativeEnum(AppDistribution),
});

export async function loader({ request }: LoaderFunctionArgs) {
  const query = parseQuery(request, QuerySchema);

  switch (query.distribution) {
    case AppDistribution.WEB:
      // We need to add this version header explicitly here as it will
      // be used in site selection to figure out if we're using the
      // correct versions here.
      return redirect(`/app/workspace`, {
        headers: {
          [VERSION_HEADER]: GLOBAL_PROPERTIES.version,
        },
      });
    case AppDistribution.MAC_WEB:
      return redirect(
        `${GLOBAL_PROPERTIES.appsStorageUrl}/v${GLOBAL_PROPERTIES.version}/Thrive-${GLOBAL_PROPERTIES.version}-universal.dmg`,
      );
    case AppDistribution.MAC_STORE:
      return redirect(GLOBAL_PROPERTIES.macStoreUrl);
    case AppDistribution.APP_STORE:
      return redirect(GLOBAL_PROPERTIES.appStoreUrl);
    case AppDistribution.GOOGLE_PLAY_STORE:
      return redirect(GLOBAL_PROPERTIES.googlePlayStoreUrl);
    default:
      // Return a 404
      throw new Response(null, {
        status: 404,
        statusText: "Not Found",
      });
  }
}
