import { Env } from "jupiter-gen";

export function isDevelopment(env: Env) {
  return env !== Env.PRODUCTION;
}
