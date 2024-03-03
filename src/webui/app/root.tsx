import { createTheme, CssBaseline, ThemeProvider } from "@mui/material";
import type { SerializeFrom } from "@remix-run/node";
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
import { EnvBanner } from "./components/infra/env-banner";
import {
  GlobalPropertiesContext,
  serverToClientGlobalProperties,
} from "./global-properties-client";
import { GLOBAL_PROPERTIES } from "./global-properties-server";
import { standardShouldRevalidate } from "./rendering/standard-should-revalidate";

const THEME = createTheme({});

export async function loader() {
  return json({
    globalProperties: serverToClientGlobalProperties(GLOBAL_PROPERTIES),
  });
}

export function meta({ data }: { data: SerializeFrom<typeof loader> }) {
  return {
    charset: "utf-8",
    title: data.globalProperties.title,
    viewport: "width=device-width,initial-scale=1",
  };
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function App() {
  const loaderData = useLoaderData<typeof loader>();

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
