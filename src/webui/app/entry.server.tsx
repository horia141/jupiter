import type { EntryContext } from "@remix-run/node";
import { Response } from "@remix-run/node";
import { RemixServer } from "@remix-run/react";
import { renderToPipeableStream } from "react-dom/server";
import { PassThrough } from "stream";
import { GLOBAL_PROPERTIES } from "./global-properties-server";
import { ENV_HEADER, HOSTING_HEADER, VERSION_HEADER } from "./names";

const ABORT_DELAY = 5000;

export default function handleRequest(
  request: Request,
  responseStatusCode: number,
  responseHeaders: Headers,
  remixContext: EntryContext
) {
  return new Promise((resolve, reject) => {
    let didError = false;
    let done = false;

    const { pipe, abort } = renderToPipeableStream(
      <RemixServer context={remixContext} url={request.url} />,
      {
        onShellReady() {
          const body = new PassThrough();

          responseHeaders.set("Content-Type", "text/html");
          responseHeaders.set(ENV_HEADER, GLOBAL_PROPERTIES.env);
          responseHeaders.set(HOSTING_HEADER, GLOBAL_PROPERTIES.hosting);
          responseHeaders.set(VERSION_HEADER, GLOBAL_PROPERTIES.version);

          done = true;

          resolve(
            new Response(body, {
              headers: responseHeaders,
              status: didError ? 500 : responseStatusCode,
            })
          );

          pipe(body);
        },
        onShellError(error: unknown) {
          done = true;
          reject(error);
        },
        onError(error: unknown) {
          didError = true;
          done = true;

          console.error(error);
        },
      }
    );

    setTimeout(() => {
      if (!done) {
        abort();
      }
    }, ABORT_DELAY);
  });
}
