import { HabitRepeatsStrategy } from "@jupiter/webapi-client";

export function strategyName(strategy: HabitRepeatsStrategy): string {
  switch (strategy) {
    case HabitRepeatsStrategy.ALL_SAME:
      return "Same Time";
    case HabitRepeatsStrategy.SPREAD_OUT_NO_OVERLAP:
      return "Spread Out";
  }
}
