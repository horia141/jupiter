import type { User, UserFeature } from "jupiter-gen";

export function isUserFeatureAvailable(
  user: User,
  feature: UserFeature
): boolean {
  return user.feature_flags[feature];
}
