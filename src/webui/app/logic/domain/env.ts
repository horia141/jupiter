import { Env } from "jupiter-gen";

export function isDevelopment(env: Env) {
  return env !== Env.PRODUCTION;
}

export function isLocal(env: Env) {
  return env === Env.LOCAL;
}
