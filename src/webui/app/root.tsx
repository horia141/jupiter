import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import type { LoaderFunctionArgs, SerializeFrom } from "@remix-run/node";
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
import { StrictMode } from "react";

import { EnvBanner } from "~/components/infra/env-banner";
import { serverToClientGlobalProperties } from "~/global-properties-client";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";
import { loadFrontDoorInfo } from "~/logic/frontdoor.server";

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

export async function loader({ request }: LoaderFunctionArgs) {
  // This is the only place where we can read this field.
  const frontDoor = await loadFrontDoorInfo(
    GLOBAL_PROPERTIES.version,
    request.headers.get("Cookie"),
    request.headers.get("User-Agent"),
  );

  return json({
    globalProperties: serverToClientGlobalProperties(
      GLOBAL_PROPERTIES,
      frontDoor,
    ),
  });
}

export function meta({ data }: { data: SerializeFrom<typeof loader> }) {
  return [{ charset: "utf-8" }, { title: data.globalProperties.title }];
}

export function links() {
  return [{ rel: "manifest", href: "/pwa-manifest" }];
}

export const shouldRevalidate: ShouldRevalidateFunction = () => false;

export default function Root() {
  const loaderData = useLoaderData<typeof loader>();
  return (
    <html lang="en">
      <head>
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no"
        />
        <Meta />
        <Links />
      </head>
      <body>
        <StrictMode>
          <ThemeProvider theme={THEME}>
            <SnackbarProvider>
              <CssBaseline />
              <EnvBanner env={loaderData.globalProperties.env} />
              <Outlet />
            </SnackbarProvider>
          </ThemeProvider>
        </StrictMode>
        <Scripts />
        <LiveReload />
      </body>
    </html>
  );
}
