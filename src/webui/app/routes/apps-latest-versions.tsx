import type { LoaderArgs } from "@remix-run/node";
import { redirect } from "@remix-run/node";
import { z } from "zod";
import { parseQuery } from "zodix";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";

const QuerySchema = {
  platform: z.enum(["darwin", "mas"]),
};

export async function loader({ request }: LoaderArgs) {
  const query = parseQuery(request, QuerySchema);

  switch (query.platform) {
    case "darwin":
      return redirect(
        `${GLOBAL_PROPERTIES.appsStorageUrl}/v${GLOBAL_PROPERTIES.version}/Thrive-${GLOBAL_PROPERTIES.version}-universal.dmg`
      );
    case "mas":
      return redirect(
        `${GLOBAL_PROPERTIES.appsStorageUrl}/v${GLOBAL_PROPERTIES.version}/Thrive-${GLOBAL_PROPERTIES.version}-universal.pkg`
      );
  }
}
