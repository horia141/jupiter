import type { User, UserFeature } from "@jupiter/webapi-client";

export function isUserFeatureAvailable(
  user: User,
  feature: UserFeature,
): boolean {
  return user.feature_flags[feature];
}
