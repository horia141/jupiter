import { ApiClient, Hosting } from "@jupiter/webapi-client";
import type { Session } from "@remix-run/node";
import { redirect } from "@remix-run/node";
import { GLOBAL_PROPERTIES } from "./global-properties-server";

const _API_CLIENTS_BY_SESSION = new Map<undefined | string, ApiClient>();

// @secureFn
export function getGuestApiClient(session?: Session): ApiClient {
  let token = undefined;
  if (session !== undefined && session.has("authTokenExt")) {
    token = session.get("authTokenExt");
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
  });

  _API_CLIENTS_BY_SESSION.set(token?.auth_token_str, newApiClient);

  return newApiClient;
}

// @secureFn
export function getLoggedInApiClient(session: Session): ApiClient {
  if (!session.has("authTokenExt")) {
    throw redirect("/login");
  }

  const authTokenExtStr = session.get("authTokenExt");

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
  });

  _API_CLIENTS_BY_SESSION.set(authTokenExtStr, newApiClient);

  return newApiClient;
}
