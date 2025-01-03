import { ApiClient, Hosting } from "@jupiter/webapi-client";
import { redirect } from "@remix-run/node";
import { GLOBAL_PROPERTIES } from "./global-properties-server";
import { loadFrontDoorInfo } from "./logic/frontdoor.server";
import { AUTH_TOKEN_NAME, FRONTDOOR_HEADER } from "./names";
import { getSession } from "./sessions";

const _API_CLIENTS_BY_SESSION = new Map<undefined | string, ApiClient>();

// @secureFn
export async function getGuestApiClient(request: Request): Promise<ApiClient> {
  const session = await getSession(request.headers.get("Cookie"));
  const frontDoor = await loadFrontDoorInfo(
    request.headers.get("Cookie"),
    request.headers.get("User-Agent")
  );

  let token = undefined;
  if (session !== undefined && session.has(AUTH_TOKEN_NAME)) {
    token = session.get(AUTH_TOKEN_NAME);
  }

  if (_API_CLIENTS_BY_SESSION.has(token)) {
    return _API_CLIENTS_BY_SESSION.get(token) as ApiClient;
  }

  let base = "";
  if (GLOBAL_PROPERTIES.hosting === Hosting.LOCAL) {
    base = GLOBAL_PROPERTIES.localWebApiServerUrl;
  } else if (GLOBAL_PROPERTIES.hosting === Hosting.HOSTED_GLOBAL) {
    base = GLOBAL_PROPERTIES.hostedGlobalWebApiServerUrl;
  } else {
    throw new Error("Unknown hosting: " + GLOBAL_PROPERTIES.hosting);
  }

  const newApiClient = new ApiClient({
    BASE: base,
    TOKEN: token,
    HEADERS: {
      [FRONTDOOR_HEADER]: `${frontDoor.appShell}:${frontDoor.appPlatform}:${frontDoor.appDistribution}`,
    },
  });

  _API_CLIENTS_BY_SESSION.set(token, newApiClient);

  return newApiClient;
}

// @secureFn
export async function getLoggedInApiClient(
  request: Request
): Promise<ApiClient> {
  const session = await getSession(request.headers.get("Cookie"));
  const frontDoor = await loadFrontDoorInfo(
    request.headers.get("Cookie"),
    request.headers.get("User-Agent")
  );

  if (!session.has(AUTH_TOKEN_NAME)) {
    throw redirect("/login");
  }

  const authTokenExtStr = session.get(AUTH_TOKEN_NAME);

  if (_API_CLIENTS_BY_SESSION.has(authTokenExtStr)) {
    return _API_CLIENTS_BY_SESSION.get(authTokenExtStr) as ApiClient;
  }

  let base = "";
  if (GLOBAL_PROPERTIES.hosting === Hosting.LOCAL) {
    base = GLOBAL_PROPERTIES.localWebApiServerUrl;
  } else if (GLOBAL_PROPERTIES.hosting === Hosting.HOSTED_GLOBAL) {
    base = GLOBAL_PROPERTIES.hostedGlobalWebApiServerUrl;
  } else {
    throw new Error("Unknown hosting option: " + GLOBAL_PROPERTIES.hosting);
  }

  const newApiClient = new ApiClient({
    BASE: base,
    TOKEN: authTokenExtStr,
    HEADERS: {
      [FRONTDOOR_HEADER]: `${frontDoor.appShell}:${frontDoor.appPlatform}:${frontDoor.appDistribution}`,
    },
  });

  _API_CLIENTS_BY_SESSION.set(authTokenExtStr, newApiClient);

  return newApiClient;
}
