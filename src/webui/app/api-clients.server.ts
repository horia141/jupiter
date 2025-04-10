import { ApiClient, Hosting } from "@jupiter/webapi-client";
import { redirect } from "@remix-run/node";

import { GLOBAL_PROPERTIES } from "./global-properties-server";
import type { FrontDoorInfo } from "./logic/frontdoor";
import { loadFrontDoorInfo } from "./logic/frontdoor.server";
import { AUTH_TOKEN_NAME, FRONTDOOR_HEADER } from "./names";
import { getSession } from "./sessions";

const _API_CLIENTS_BY_SESSION = new Map<undefined | string, ApiClient>();

// @secureFn
export async function getGuestApiClient(
  request: Request,
  newFrontDoor?: FrontDoorInfo,
): Promise<ApiClient> {
  const session = await getSession(request.headers.get("Cookie"));
  const frontDoor =
    newFrontDoor ||
    (await loadFrontDoorInfo(
      GLOBAL_PROPERTIES.version,
      request.headers.get("Cookie"),
      request.headers.get("User-Agent"),
    ));

  let token = undefined;
  if (session !== undefined && session.has(AUTH_TOKEN_NAME)) {
    token = session.get(AUTH_TOKEN_NAME);
  }

  if (_API_CLIENTS_BY_SESSION.has(token)) {
    return _API_CLIENTS_BY_SESSION.get(token) as ApiClient;
  }

  let base = "";
  if (
    GLOBAL_PROPERTIES.hosting === Hosting.LOCAL ||
    GLOBAL_PROPERTIES.hosting === Hosting.SELF_HOSTED
  ) {
    base = GLOBAL_PROPERTIES.localOrSelfHostedWebApiServerUrl;
  } else if (GLOBAL_PROPERTIES.hosting === Hosting.HOSTED_GLOBAL) {
    base = GLOBAL_PROPERTIES.hostedGlobalWebApiServerUrl;
  } else {
    throw new Error("Unknown hosting: " + GLOBAL_PROPERTIES.hosting);
  }

  const newApiClient = new ApiClient({
    BASE: base,
    TOKEN: token,
    HEADERS: {
      [FRONTDOOR_HEADER]: `${frontDoor.clientVersion}:${frontDoor.appShell}:${frontDoor.appPlatform}:${frontDoor.appDistribution}`,
    },
  });

  _API_CLIENTS_BY_SESSION.set(token, newApiClient);

  return newApiClient;
}

// @secureFn
export async function getLoggedInApiClient(
  request: Request,
  newFrontDoor?: FrontDoorInfo,
): Promise<ApiClient> {
  const session = await getSession(request.headers.get("Cookie"));
  const frontDoor =
    newFrontDoor ||
    (await loadFrontDoorInfo(
      GLOBAL_PROPERTIES.version,
      request.headers.get("Cookie"),
      request.headers.get("User-Agent"),
    ));

  if (!session.has(AUTH_TOKEN_NAME)) {
    throw redirect("/app/login");
  }

  const authTokenExtStr = session.get(AUTH_TOKEN_NAME);

  if (_API_CLIENTS_BY_SESSION.has(authTokenExtStr)) {
    return _API_CLIENTS_BY_SESSION.get(authTokenExtStr) as ApiClient;
  }

  let base = "";
  if (
    GLOBAL_PROPERTIES.hosting === Hosting.LOCAL ||
    GLOBAL_PROPERTIES.hosting === Hosting.SELF_HOSTED
  ) {
    base = GLOBAL_PROPERTIES.localOrSelfHostedWebApiServerUrl;
  } else if (GLOBAL_PROPERTIES.hosting === Hosting.HOSTED_GLOBAL) {
    base = GLOBAL_PROPERTIES.hostedGlobalWebApiServerUrl;
  } else {
    throw new Error("Unknown hosting option: " + GLOBAL_PROPERTIES.hosting);
  }

  const newApiClient = new ApiClient({
    BASE: base,
    TOKEN: authTokenExtStr,
    HEADERS: {
      [FRONTDOOR_HEADER]: `${frontDoor.clientVersion}:${frontDoor.appShell}:${frontDoor.appPlatform}:${frontDoor.appDistribution}`,
    },
  });

  _API_CLIENTS_BY_SESSION.set(authTokenExtStr, newApiClient);

  return newApiClient;
}
