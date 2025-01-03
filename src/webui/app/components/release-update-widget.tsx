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
  styled,
  Typography,
} from "@mui/material";
import { useFetcher } from "@remix-run/react";
import { useContext, useEffect, useState } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import type { ReleaseManifestResult } from "~/logic/release";

const REFRESH_INTERVAL_MS = 5 * 1000;

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

  const releaseManifestResult: ReleaseManifestResult =
    releaseManifestFetcher.data;

  if (releaseManifestResult.latestServerVersion === globalProperties.version) {
    return <></>;
  }

  const reloadButton = (
    <Button
      variant="contained"
      color="primary"
      onClick={() => window.location.reload()}
    >
      Update
    </Button>
  );
  const downloadButton = (
    <Button
      variant="contained"
      color="primary"
      component={"a"}
      target="_blank"
      href={`/apps-latest-versions?distribution=${globalProperties.frontDoorInfo.appDistribution}`}
    >
      Update
    </Button>
  );
  const cantUpdateButton = (
    <Button variant="contained" color="primary" disabled>
      Can't Update
    </Button>
  );

  let action = null;

  switch (globalProperties.frontDoorInfo.appShell) {
    case AppShell.BROWSER:
    case AppShell.MOBILE_PWA:
      action = reloadButton;
      break;
    case AppShell.DESKTOP_ELECTRON:
      switch (globalProperties.frontDoorInfo.appDistribution) {
        case AppDistribution.MAC_WEB:
          if (
            releaseManifestResult.manifest[AppDistribution.MAC_WEB] ===
            AppDistributionState.READY
          ) {
            action = downloadButton;
          } else {
            action = reloadButton;
          }
          break;
        case AppDistribution.MAC_STORE:
          if (
            releaseManifestResult.manifest[AppDistribution.MAC_STORE] ===
            AppDistributionState.READY
          ) {
            action = downloadButton;
          } else {
            action = reloadButton;
          }
          break;
        default:
          action = cantUpdateButton;
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
            action = downloadButton;
          } else {
            action = reloadButton;
          }
          break;
        case AppPlatform.MOBILE_ANDROID:
        case AppPlatform.TABLET_ANDROID:
          if (
            releaseManifestResult.manifest[
              AppDistribution.GOOGLE_PLAY_STORE
            ] === AppDistributionState.READY
          ) {
            action = downloadButton;
          } else {
            action = reloadButton;
          }
          break;
        default:
          action = cantUpdateButton;
      }
      break;
    default:
      action = cantUpdateButton;
  }

  return (
    <StyledFloatingBox>
      <Card>
        <CardContent>
          <Typography variant="body1">
            There is an update available. Press update to trigger it!
          </Typography>
        </CardContent>
        <CardActions>
          {action}
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

const StyledFloatingBox = styled(Box)({
  position: "fixed",
  bottom: 0,
  left: "calc(50% - 150px)",
  width: "300px",
  marginBottom: "1rem",
  padding: "1rem",
  borderRadius: "1rem",
});
