import { Env } from "@jupiter/webapi-client";

export function isDevelopment(env: Env) {
  return env !== Env.PRODUCTION;
}

export function isLocal(env: Env) {
  return env === Env.LOCAL;
}
