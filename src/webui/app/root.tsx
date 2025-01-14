import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import type { LoaderArgs, SerializeFrom } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  useLoaderData,
} from "@remix-run/react";
import { SnackbarProvider } from "notistack";

import { SplashScreen } from "@capacitor/splash-screen";
import { AppShell } from "@jupiter/webapi-client";
import { StrictMode, useEffect } from "react";
import { EnvBanner } from "./components/infra/env-banner";
import {
  GlobalPropertiesContext,
  serverToClientGlobalProperties,
} from "./global-properties-client";
import { GLOBAL_PROPERTIES } from "./global-properties-server";
import { loadFrontDoorInfo } from "./logic/frontdoor.server";
import { standardShouldRevalidate } from "./rendering/standard-should-revalidate";

const THEME = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#3F51B5",
      light: "#7986CB",
      dark: "#303F9F",
    },
    secondary: {
      main: "#FF4081",
      light: "#FF79B0",
      dark: "#C60055",
    },
    divider: "#E0E0E0",
    text: {
      primary: "#212121",
      secondary: "#757575",
      disabled: "#BDBDBD",
    },
  },
  typography: {
    fontFamily: '"Helvetica", "Arial", sans-serif',
  },
});

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

export function meta({ data }: { data: SerializeFrom<typeof loader> }) {
  return {
    charset: "utf-8",
    title: data.globalProperties.title,
    viewport:
      "width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no",
  };
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function App() {
  const loaderData = useLoaderData<typeof loader>();

  useEffect(() => {
    if (
      loaderData.globalProperties.frontDoorInfo.appShell ===
      AppShell.MOBILE_CAPACITOR
    ) {
      SplashScreen.hide();
    }
  }, [loaderData.globalProperties.frontDoorInfo.appShell]);

  return (
    <html lang="en">
      <head>
        <Meta />
        <Links />
      </head>
      <body>
        <StrictMode>
          <GlobalPropertiesContext.Provider value={loaderData.globalProperties}>
            <ThemeProvider theme={THEME}>
              <SnackbarProvider>
                <CssBaseline />
                <EnvBanner />
                <Outlet />
              </SnackbarProvider>
            </ThemeProvider>
          </GlobalPropertiesContext.Provider>
        </StrictMode>
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}
