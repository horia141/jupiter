import { Hosting } from "@jupiter/webapi-client";

export function hostingName(hosting: Hosting): string {
  switch (hosting) {
    case Hosting.LOCAL:
      return "Local";
    case Hosting.HOSTED_GLOBAL:
      return "Hosted globally";
  }
}
