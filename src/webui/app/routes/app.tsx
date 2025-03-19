import { App as CapacitorApp } from "@capacitor/app";
import { SplashScreen } from "@capacitor/splash-screen";
import { AppPlatform, AppShell } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useLoaderData, useNavigate } from "@remix-run/react";
import { useEffect } from "react";
import {
  GlobalPropertiesContext,
  serverToClientGlobalProperties,
} from "~/global-properties-client";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { loadFrontDoorInfo } from "~/logic/frontdoor.server";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";

export async function loader({ request }: LoaderArgs) {
  // This is the only place where we can read this field.
  const frontDoor = await loadFrontDoorInfo(
    GLOBAL_PROPERTIES.version,
    request.headers.get("Cookie"),
    request.headers.get("User-Agent")
  );

  return json({
    globalProperties: serverToClientGlobalProperties(
      GLOBAL_PROPERTIES,
      frontDoor
    ),
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function App() {
  const loaderData = useLoaderData<typeof loader>();
  const navigate = useNavigate();

  useEffect(() => {
    if (
      loaderData.globalProperties.frontDoorInfo.appShell ===
      AppShell.MOBILE_CAPACITOR
    ) {
      SplashScreen.hide();
    }

    if (
      loaderData.globalProperties.frontDoorInfo.appPlatform ===
        AppPlatform.MOBILE_ANDROID ||
      loaderData.globalProperties.frontDoorInfo.appPlatform ===
        AppPlatform.TABLET_ANDROID
    ) {
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

      setupBackButton();
    }
  }, [loaderData.globalProperties.frontDoorInfo, navigate]);

  return (
    <GlobalPropertiesContext.Provider value={loaderData.globalProperties}>
      <Outlet />
    </GlobalPropertiesContext.Provider>
  );
}
