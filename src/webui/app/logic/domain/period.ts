import { RecurringTaskPeriod } from "@jupiter/webapi-client";

export function periodName(
  status: RecurringTaskPeriod,
  isBigScreen: boolean = true
): string {
  switch (status) {
    case RecurringTaskPeriod.DAILY:
      return isBigScreen ? "Daily" : "Day";
    case RecurringTaskPeriod.WEEKLY:
      return isBigScreen ? "Weekly" : "Wk";
    case RecurringTaskPeriod.MONTHLY:
      return isBigScreen ? "Monthly" : "Mnth";
    case RecurringTaskPeriod.QUARTERLY:
      return isBigScreen ? "Quarterly" : "Qrt";
    case RecurringTaskPeriod.YEARLY:
      return isBigScreen ? "Year" : "Yr";
  }
}

const PERIOD_MAP = {
  [RecurringTaskPeriod.DAILY]: 0,
  [RecurringTaskPeriod.WEEKLY]: 1,
  [RecurringTaskPeriod.MONTHLY]: 2,
  [RecurringTaskPeriod.QUARTERLY]: 3,
  [RecurringTaskPeriod.YEARLY]: 4,
};

export function oneLessThanPeriod(
  period: RecurringTaskPeriod
): RecurringTaskPeriod {
  switch (period) {
    case RecurringTaskPeriod.DAILY:
      throw new Error(`Invalid period ${period} for computing one less`);
    case RecurringTaskPeriod.WEEKLY:
      return RecurringTaskPeriod.DAILY;
    case RecurringTaskPeriod.MONTHLY:
      return RecurringTaskPeriod.WEEKLY;
    case RecurringTaskPeriod.QUARTERLY:
      return RecurringTaskPeriod.MONTHLY;
    case RecurringTaskPeriod.YEARLY:
      return RecurringTaskPeriod.QUARTERLY;
  }
}

export function oneMoreThanPeriod(
  period: RecurringTaskPeriod
): RecurringTaskPeriod {
  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return RecurringTaskPeriod.WEEKLY;
    case RecurringTaskPeriod.WEEKLY:
      return RecurringTaskPeriod.MONTHLY;
    case RecurringTaskPeriod.MONTHLY:
      return RecurringTaskPeriod.QUARTERLY;
    case RecurringTaskPeriod.QUARTERLY:
      return RecurringTaskPeriod.YEARLY;
    case RecurringTaskPeriod.YEARLY:
      throw new Error(`Invalid period ${period} for computing one more`);
  }
}

export function comparePeriods(
  period1: RecurringTaskPeriod,
  period2: RecurringTaskPeriod
): number {
  return PERIOD_MAP[period1] - PERIOD_MAP[period2];
}
