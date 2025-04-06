import { Hosting } from "@jupiter/webapi-client";

export function isInGlobalHosting(hosting: Hosting): boolean {
  return hosting === Hosting.HOSTED_GLOBAL;
}

export function hostingName(hosting: Hosting): string {
  switch (hosting) {
    case Hosting.LOCAL:
      return "Local";
    case Hosting.HOSTED_GLOBAL:
      return "Hosted globally";
    case Hosting.SELF_HOSTED:
      return "Self-hosted";
  }
}
