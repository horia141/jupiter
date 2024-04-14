import { RemixBrowser } from "@remix-run/react";
import { startTransition, StrictMode } from "react";
import { hydrateRoot } from "react-dom/client";

function hydrate() {
  // Remove all elements added by extensions of various sorts, or by
  // playwrights infra. This is necessary because we don't want to
  // cause hydration mismatches.
  // The rabbit hole goes deep: https://github.com/facebook/react/issues/24430
  document.querySelectorAll('html > script, html > x-pw-glass').forEach((s) => {
    s.parentNode?.removeChild(s);
  });

  startTransition(() => {
    hydrateRoot(
      document,
      <StrictMode>
        <RemixBrowser />
      </StrictMode>
    );
  });
}

if (window.requestIdleCallback) {
  window.requestIdleCallback(hydrate);
} else {
  // Safari doesn't support requestIdleCallback
  // https://caniuse.com/requestidlecallback
  window.setTimeout(hydrate, 1);
}
