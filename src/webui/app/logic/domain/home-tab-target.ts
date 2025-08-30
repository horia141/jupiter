import { HomeTabTarget } from "@jupiter/webapi-client";

export function homeTabTargetName(target: HomeTabTarget): string {
  switch (target) {
    case HomeTabTarget.BIG_SCREEN:
      return "Big Screen";
    case HomeTabTarget.SMALL_SCREEN:
      return "Small Screen";
  }
}
