import {
  AppDistribution,
  AppDistributionState,
  AppPlatform,
  AppShell,
} from "@jupiter/webapi-client";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Typography,
  styled,
} from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { useContext, useEffect, useState } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import type { ReleaseManifestResult } from "~/logic/release";

const REFRESH_INTERVAL_MS = 5 * 60 * 1000;

export function ReleaseUpdateWidget() {
  const releaseManifestFetcher = useFetcher<ReleaseManifestResult>();
  const globalProperties = useContext(GlobalPropertiesContext);
  const [dismiss, setDismiss] = useState(false);

  useEffect(() => {
    const intervalId = setInterval(() => {
      releaseManifestFetcher.load("/release-manifest");
    }, REFRESH_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [releaseManifestFetcher]);

  if (dismiss) {
    return <></>;
  }

  if (releaseManifestFetcher.data === undefined) {
    return <></>;
  }

  if (
    releaseManifestFetcher.data.ok === false ||
    !releaseManifestFetcher.data.res
  ) {
    return <></>;
  }

  const releaseManifestResult = releaseManifestFetcher.data.res;

  // First thing we check is if the latest server version is different from the client version.
  //   * Typically, we release a new version of the app much rarer than we do a new release of webui.
  //     The app shells have versions baked in them, and they know this as the client version. Which
  //     is typically the same or behind the main version.
  //   * If there's a new app shell version, we should show the download button.
  // So if this is the case, we then check if there's a ready distribution.
  // If there is, we will show the download button.
  // If there isn't, we continue the analysis.
  if (
    releaseManifestResult.latestServerVersion !==
    globalProperties.frontDoorInfo.clientVersion
  ) {
    let action = false;

    switch (globalProperties.frontDoorInfo.appShell) {
      case AppShell.BROWSER:
      case AppShell.PWA:
        break;

      case AppShell.DESKTOP_ELECTRON:
        switch (globalProperties.frontDoorInfo.appDistribution) {
          case AppDistribution.MAC_WEB:
            if (
              releaseManifestResult.manifest[AppDistribution.MAC_WEB] ===
              AppDistributionState.READY
            ) {
              action = true;
            }
            break;
          case AppDistribution.MAC_STORE:
            if (
              releaseManifestResult.manifest[AppDistribution.MAC_STORE] ===
              AppDistributionState.READY
            ) {
              action = true;
            }
            break;
        }
        break;
      case AppShell.MOBILE_CAPACITOR:
        switch (globalProperties.frontDoorInfo.appPlatform) {
          case AppPlatform.MOBILE_IOS:
          case AppPlatform.TABLET_IOS:
            if (
              releaseManifestResult.manifest[AppDistribution.APP_STORE] ===
              AppDistributionState.READY
            ) {
              action = true;
            }
            break;
          case AppPlatform.MOBILE_ANDROID:
          case AppPlatform.TABLET_ANDROID:
            if (
              releaseManifestResult.manifest[
                AppDistribution.GOOGLE_PLAY_STORE
              ] === AppDistributionState.READY
            ) {
              action = true;
            }
            break;
        }
        break;
    }

    if (action) {
      return (
        <StyledFloatingBox>
          <Card>
            <CardContent>
              <Typography variant="body1">
                There is a new app version available. Press update to download
                it!
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                variant="contained"
                color="primary"
                component={"a"}
                target="_blank"
                href={`/apps-latest-versions?distribution=${globalProperties.frontDoorInfo.appDistribution}`}
              >
                Download
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => setDismiss(true)}
              >
                Dismiss
              </Button>
            </CardActions>
          </Card>
        </StyledFloatingBox>
      );
    }
  }

  // If we don't have any new app to download, perhaps there's a new webui version.
  // This means that the core that's running locally inside the app shell needs a reload.
  if (releaseManifestResult.latestServerVersion !== globalProperties.version) {
    return (
      <StyledFloatingBox>
        <Card>
          <CardContent>
            <Typography variant="body1">
              There is an update available. Press update to trigger it!
            </Typography>
          </CardContent>
          <CardActions>
            <Button
              variant="contained"
              color="primary"
              onClick={() => window.location.reload()}
            >
              Update
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => setDismiss(true)}
            >
              Dismiss
            </Button>
          </CardActions>
        </Card>
      </StyledFloatingBox>
    );
  }

  // Nothing to update!
  return <></>;
}

const StyledFloatingBox = styled(Box)({
  position: "fixed",
  bottom: 0,
  left: "calc(50% - 150px)",
  width: "300px",
  marginBottom: "1rem",
  padding: "1rem",
  borderRadius: "1rem",
});
