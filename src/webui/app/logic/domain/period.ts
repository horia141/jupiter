import { RecurringTaskPeriod } from "@jupiter/webapi-client";

export function periodName(status: RecurringTaskPeriod): string {
  switch (status) {
    case RecurringTaskPeriod.DAILY:
      return "Daily";
    case RecurringTaskPeriod.WEEKLY:
      return "Weekly";
    case RecurringTaskPeriod.MONTHLY:
      return "Monthly";
    case RecurringTaskPeriod.QUARTERLY:
      return "Quarterly";
    case RecurringTaskPeriod.YEARLY:
      return "Yearly";
  }
}

const PERIOD_MAP = {
  [RecurringTaskPeriod.DAILY]: 0,
  [RecurringTaskPeriod.WEEKLY]: 1,
  [RecurringTaskPeriod.MONTHLY]: 2,
  [RecurringTaskPeriod.QUARTERLY]: 3,
  [RecurringTaskPeriod.YEARLY]: 4,
};

export function oneLessThanPeriod(period: RecurringTaskPeriod) {
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

export function comparePeriods(
  period1: RecurringTaskPeriod,
  period2: RecurringTaskPeriod
): number {
  return PERIOD_MAP[period1] - PERIOD_MAP[period2];
}
