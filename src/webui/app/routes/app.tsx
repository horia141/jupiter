import { App as CapacitorApp } from "@capacitor/app";
import { Browser } from "@capacitor/browser";
import { SplashScreen } from "@capacitor/splash-screen";
import { AppPlatform, AppShell } from "@jupiter/webapi-client";
import type {
  LoaderFunctionArgs,
  ShouldRevalidateFunction,
} from "react-router";
import { Outlet, useLoaderData, useNavigate } from "react-router";
import { useEffect } from "react";
import {
  GlobalPropertiesContext,
  serverToClientGlobalProperties,
} from "@jupiter/core/config-client";
import { GLOBAL_PROPERTIES } from "@jupiter/core/config-server";
import { FrontDoorInfoContext } from "@jupiter/core/infra/frontdoor-info-context";
import { GoogleMapsApiKeyContext } from "@jupiter/core/infra/google-maps-api-key-context";
import { OverdueThresholdsContext } from "@jupiter/core/infra/overdue-thresholds-context";
import { ServiceLinksContext } from "@jupiter/core/infra/service-links-context";
import { hasShellFeature, ShellFeature } from "@jupiter/core/frontdoor";
import { loadFrontDoorInfo } from "@jupiter/core/frontdoor.server";

import { ServicePropertiesContext } from "~/logic/config";
import {
  SERVICE_PROPERTIES,
  serverToClientServiceProperties,
} from "~/logic/config.server";

export async function loader({ request }: LoaderFunctionArgs) {
  // This is the only place where we can read this field.
  const frontDoor = await loadFrontDoorInfo(
    GLOBAL_PROPERTIES.version,
    request.headers.get("Cookie"),
    request.headers.get("User-Agent"),
  );

  return {
    globalProperties: serverToClientGlobalProperties(GLOBAL_PROPERTIES),
    serviceProperties: serverToClientServiceProperties(
      SERVICE_PROPERTIES,
      frontDoor,
    ),
  };
}

export const shouldRevalidate: ShouldRevalidateFunction = () => false;

export default function App() {
  const loaderData = useLoaderData<typeof loader>();
  const navigate = useNavigate();

  useEffect(() => {
    if (
      loaderData.serviceProperties.frontDoorInfo.appShell ===
      AppShell.MOBILE_CAPACITOR
    ) {
      SplashScreen.hide();
    }

    async function setupBackButton() {
      const backHandler = await CapacitorApp.addListener("backButton", () => {
        if (window.history.state?.idx > 0) {
          navigate(-1);
        } else {
          CapacitorApp.exitApp();
        }
      });

      return () => {
        backHandler.remove();
      };
    }

    if (
      loaderData.serviceProperties.frontDoorInfo.appPlatform ===
        AppPlatform.MOBILE_ANDROID ||
      loaderData.serviceProperties.frontDoorInfo.appPlatform ===
        AppPlatform.TABLET_ANDROID
    ) {
      setupBackButton();
    }
  }, [loaderData.serviceProperties.frontDoorInfo, navigate]);

  useEffect(() => {
    // The mobile shell lets the webview go to any server, so a link to
    // another site would open inside the app with no way back. Send those to
    // the system browser instead.
    if (
      !hasShellFeature(
        loaderData.serviceProperties.frontDoorInfo,
        ShellFeature.EXTERNAL_BROWSER,
      )
    ) {
      return;
    }

    function handleClick(event: MouseEvent) {
      if (event.defaultPrevented || event.button !== 0) {
        return;
      }

      const anchor = (event.target as Element | null)?.closest("a[href]");
      if (!(anchor instanceof HTMLAnchorElement)) {
        return;
      }

      const url = new URL(anchor.href, window.location.href);
      if (
        (url.protocol !== "http:" && url.protocol !== "https:") ||
        url.origin === window.location.origin
      ) {
        return;
      }

      event.preventDefault();
      Browser.open({ url: url.toString() });
    }

    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, [loaderData.serviceProperties.frontDoorInfo]);

  return (
    <GlobalPropertiesContext.Provider value={loaderData.globalProperties}>
      <ServicePropertiesContext.Provider value={loaderData.serviceProperties}>
        <FrontDoorInfoContext.Provider
          value={loaderData.serviceProperties.frontDoorInfo}
        >
          <ServiceLinksContext.Provider value={loaderData.serviceProperties}>
            <OverdueThresholdsContext.Provider
              value={loaderData.serviceProperties}
            >
              <GoogleMapsApiKeyContext.Provider
                value={loaderData.serviceProperties}
              >
                <Outlet />
              </GoogleMapsApiKeyContext.Provider>
            </OverdueThresholdsContext.Provider>
          </ServiceLinksContext.Provider>
        </FrontDoorInfoContext.Provider>
      </ServicePropertiesContext.Provider>
    </GlobalPropertiesContext.Provider>
  );
}
