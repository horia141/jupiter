import { DateTime } from "luxon";

export enum ActionableTime {
  NOW = "now",
  ONE_WEEK = "one-week",
  ONE_MONTH = "one-month",
}

export function actionableTimeToDateTime(actionableTime: ActionableTime) {
  switch (actionableTime) {
    case ActionableTime.NOW:
      return DateTime.now();
    case ActionableTime.ONE_WEEK:
      return DateTime.now().plus({ weeks: 1 });
    case ActionableTime.ONE_MONTH:
      return DateTime.now().plus({ months: 1 });
  }
}
