import { createTheme, CssBaseline, styled, ThemeProvider } from "@mui/material";
import { json } from "@remix-run/node";
import {
  Links,
  LiveReload,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  ShouldRevalidateFunction,
  useLoaderData,
} from "@remix-run/react";
import {SnackbarProvider} from "notistack";

import { StrictMode } from "react";
import ScrollToTop from "react-scroll-to-top";
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

export function meta() {
  return {
    charset: "utf-8",
    title: "Jupiter",
    viewport: "width=device-width,initial-scale=1",
  };
}

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function App() {
  const loaderData = useLoaderData<typeof loader>();

  return (
    <html lang="en">
      <head>
        <Meta />
        <Links />
      </head>
      <BodyWithNoScroll>
        <StrictMode>
          <GlobalPropertiesContext.Provider value={loaderData.globalProperties}>
            <ThemeProvider theme={THEME}>
              <SnackbarProvider>
              <CssBaseline />
              <EnvBanner />
              <ScrollToTop
                smooth
                style={{
                  zIndex: THEME.zIndex.appBar + 1,
                  width: "4rem",
                  height: "4rem",
                }}
              />
              <Outlet />
              </SnackbarProvider>
            </ThemeProvider>
          </GlobalPropertiesContext.Provider>
        </StrictMode>
        <ScrollRestoration />
        <Scripts />
        <LiveReload />
      </BodyWithNoScroll>
    </html>
  );
}

const BodyWithNoScroll = styled("body")({
  scrollbarWidth: "none",
  msOverflowStyle: "none",
  "::-webkit-scrollbar": {
    display: "none",
    width: 0,
    color: "transparent",
  },
});
