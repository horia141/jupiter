import type { Timezone } from "@jupiter/webapi-client";
import { DateTime } from "luxon";

export enum ActionableTime {
  NOW = "now",
  ONE_WEEK = "one-week",
  ONE_MONTH = "one-month",
}

export function actionableTimeToDateTime(
  actionableTime: ActionableTime,
  timezone: Timezone
): DateTime {
  switch (actionableTime) {
    case ActionableTime.NOW:
      return DateTime.local({ zone: timezone });
    case ActionableTime.ONE_WEEK:
      return DateTime.local({ zone: timezone }).plus({ weeks: 1 });
    case ActionableTime.ONE_MONTH:
      return DateTime.local({ zone: timezone }).plus({ months: 1 });
  }
}
