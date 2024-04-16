import type { User, UserFeature } from "webapi-client";

export function isUserFeatureAvailable(
  user: User,
  feature: UserFeature
): boolean {
  return user.feature_flags[feature];
}
