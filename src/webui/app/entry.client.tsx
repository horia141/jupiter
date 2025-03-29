import { RemixBrowser } from "@remix-run/react";
import { Buffer } from "buffer-polyfill";
import { StrictMode, startTransition } from "react";
import { hydrateRoot } from "react-dom/client";

function hydrate() {
  startTransition(() => {
    hydrateRoot(
      document,
      <StrictMode>
        <RemixBrowser />
      </StrictMode>,
    );
  });
}

// Remove all elements added by extensions of various sorts, or by
// playwrights infra. This is necessary because we don't want to
// cause hydration mismatches.
// The rabbit hole goes deep: https://github.com/facebook/react/issues/24430

document
  .querySelectorAll(
    [
      "html > *:not(body, head)",
      'script[src*="extension://"]',
      'link[href*="extension://"]',
    ].join(", "),
  )
  .forEach((s) => {
    s.parentNode?.removeChild(s);
  });

window.onerror = (event: Event | string, url, line) => {
  if (
    typeof event === "string" &&
    (event.indexOf("Hydration failed") !== -1 ||
      event.indexOf("Minified React error") !== -1)
  ) {
    // We're handling some sort of React hydration error because of
    // mismatches in SSR and client-side rendering. These mostly occur
    // because of the many time manipulations we do client-side. Which
    // might differ from what's happening server-side, if we're not careful
    // or even if there's noticeable clock skew between the client's
    // machine and the server.
    // If this happens, Remix tends to crash hard - styles are messed up.
    // To prevent this we force a client-side reload to a very safe page. Which
    // then does a Remix reload to the final page. We're gonna log this
    // at some point.

    const destUrl = Buffer.from(
      `${window.location.pathname}?${window.location.search}`,
      "utf-8"
    ).toString("base64");
    window.location.replace(`/app/render-fix?returnTo=${destUrl}`);
    return true;
  }

  return false;
};

if (window.requestIdleCallback) {
  window.requestIdleCallback(hydrate);
} else {
  // Safari doesn't support requestIdleCallback
  // https://caniuse.com/requestidlecallback
  window.setTimeout(hydrate, 1);
}
