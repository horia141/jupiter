import { AppShell } from "@jupiter/webapi-client";
import { Typography } from "@mui/material";
import type { LoaderFunctionArgs } from "react-router";
import { redirectDocument, useLoaderData } from "react-router";
import { useEffect } from "react";
import { LifecyclePanel } from "@jupiter/core/infra/component/layout/lifecycle-panel";
import { StandaloneContainer } from "@jupiter/core/infra/component/layout/standalone-container";
import { GLOBAL_PROPERTIES } from "@jupiter/core/config-server";
import { hasShellFeature, ShellFeature } from "@jupiter/core/frontdoor";
import { loadFrontDoorInfo } from "@jupiter/core/frontdoor.server";

export async function loader({ request }: LoaderFunctionArgs) {
  const frontDoor = await loadFrontDoorInfo(
    GLOBAL_PROPERTIES.version,
    request.headers.get("Cookie"),
    request.headers.get("User-Agent"),
  );

  if (!hasShellFeature(frontDoor, ShellFeature.LOCAL_PICKER)) {
    return redirectDocument("/app/workspace");
  }

  return { appShell: frontDoor.appShell };
}

// The server picker lives in the app shells themselves (their pick-server.html),
// so it keeps working even when the picked server is down. All we do here is
// hand over to the shell's own picker.
export default function PickServer() {
  const { appShell } = useLoaderData<typeof loader>();

  useEffect(() => {
    switch (appShell) {
      case AppShell.DESKTOP_ELECTRON:
        // Electron's pages are file:// URLs, which a page from the server
        // can't navigate to, so the main process loads the picker for us.
        window.pickServer.openPicker();
        break;
      case AppShell.MOBILE_CAPACITOR:
        // Capacitor serves its pages from an origin of its own, which it
        // lets any page navigate to.
        window.location.href = `${window.WEBVIEW_SERVER_URL}/pick-server.html`;
        break;
      default:
        window.location.replace("/app/workspace");
    }
  }, [appShell]);

  return (
    <StandaloneContainer>
      <LifecyclePanel>
        <Typography>Opening the server picker…</Typography>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
