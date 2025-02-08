import {
  RecurringTaskPeriod,
  type RecurringTaskSkipRule,
} from "@jupiter/webapi-client";

export enum SkipRuleType {
  NONE = "none",
  EVEN = "even",
  ODD = "odd",
  EVERY = "every",
  CUSTOM_DAILY_REL_WEEKLY = "custom_daily_rel_weekly",
  CUSTOM_DAILY_REL_MONTHLY = "custom_daily_rel_monthly",
  CUSTOM_WEEKLY_REL_YEARLY = "custom_weekly_rel_yearly",
  CUSTOM_MONTHLY_REL_YEARLY = "custom_monthly_rel_yearly",
  CUSTOM_QUARTERLY_REL_YEARLY = "custom_quarterly_rel_yearly",
}

export interface SkipRuleNone {
  type: SkipRuleType.NONE;
}

export interface SkipRuleEven {
  type: SkipRuleType.EVEN;
}

export interface SkipRuleOdd {
  type: SkipRuleType.ODD;
}

export interface SkipRuleEvery {
  type: SkipRuleType.EVERY;
  n: number;
  k: number;
}

export interface SkipRuleCustomDailyRelWeekly {
  type: SkipRuleType.CUSTOM_DAILY_REL_WEEKLY;
  daysRelWeek: number[];
}

export interface SkipRuleCustomDailyRelMonthly {
  type: SkipRuleType.CUSTOM_DAILY_REL_MONTHLY;
  daysRelMonth: number[];
}

export interface SkipRuleCustomWeeklyRelYearly {
  type: SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY;
  weeks: number[];
}

export interface SkipRuleCustomMonthlyRelYearly {
  type: SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY;
  months: number[];
}

export interface SkipRuleCustomQuarterlyRelYearly {
  type: SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY;
  quarters: number[];
}

export type SkipRule =
  | SkipRuleNone
  | SkipRuleEven
  | SkipRuleOdd
  | SkipRuleEvery
  | SkipRuleCustomDailyRelWeekly
  | SkipRuleCustomDailyRelMonthly
  | SkipRuleCustomWeeklyRelYearly
  | SkipRuleCustomMonthlyRelYearly
  | SkipRuleCustomQuarterlyRelYearly;

export function skipRuleTypeName(
  skipRuleType: SkipRuleType,
  isBigScreen: boolean = true
): string {
  switch (skipRuleType) {
    case SkipRuleType.NONE:
      return isBigScreen ? "None" : "🚫";
    case SkipRuleType.EVEN:
      return "Even";
    case SkipRuleType.ODD:
      return "Odd";
    case SkipRuleType.EVERY:
      return `Every`;
    case SkipRuleType.CUSTOM_DAILY_REL_WEEKLY:
      return isBigScreen ? `In Week` : "Wk";
    case SkipRuleType.CUSTOM_DAILY_REL_MONTHLY:
      return isBigScreen ? `In Month` : "Mnth";
    case SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY:
      return isBigScreen ? `In Year` : "Yr";
    case SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY:
      return `Custom`;
    case SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY:
      return `Custom`;
  }
}

export function isCompatibleWithPeriod(
  skipRuleType: SkipRuleType,
  period: RecurringTaskPeriod
): boolean {
  const dailyTypes = [
    SkipRuleType.NONE,
    SkipRuleType.EVEN,
    SkipRuleType.ODD,
    SkipRuleType.EVERY,
    SkipRuleType.CUSTOM_DAILY_REL_WEEKLY,
    SkipRuleType.CUSTOM_DAILY_REL_MONTHLY,
  ];
  const weeklyTypes = [
    SkipRuleType.NONE,
    SkipRuleType.EVEN,
    SkipRuleType.ODD,
    SkipRuleType.EVERY,
    SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY,
  ];
  const monthlyTypes = [
    SkipRuleType.NONE,
    SkipRuleType.EVEN,
    SkipRuleType.ODD,
    SkipRuleType.EVERY,
    SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY,
  ];
  const quarterlyTypes = [
    SkipRuleType.NONE,
    SkipRuleType.EVEN,
    SkipRuleType.ODD,
    SkipRuleType.EVERY,
    SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY,
  ];
  const defaultTypes = [
    SkipRuleType.NONE,
    SkipRuleType.EVEN,
    SkipRuleType.ODD,
    SkipRuleType.EVERY,
  ];

  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return dailyTypes.includes(skipRuleType);
    case RecurringTaskPeriod.WEEKLY:
      return weeklyTypes.includes(skipRuleType);
    case RecurringTaskPeriod.MONTHLY:
      return monthlyTypes.includes(skipRuleType);
    case RecurringTaskPeriod.QUARTERLY:
      return quarterlyTypes.includes(skipRuleType);
    default:
      return defaultTypes.includes(skipRuleType);
  }
}

export function parseSkipRule(
  skipRule?: RecurringTaskSkipRule | null
): SkipRule {
  if (!skipRule) {
    return { type: SkipRuleType.NONE };
  }

  const parts = skipRule.split(" ");
  const type = parts[0];
  switch (type) {
    case SkipRuleType.EVEN:
      return { type: SkipRuleType.EVEN };
    case SkipRuleType.ODD:
      return { type: SkipRuleType.ODD };
    case SkipRuleType.EVERY:
      return {
        type: SkipRuleType.EVERY,
        n: parseInt(parts[1]),
        k: parseInt(parts[2]),
      };
    case SkipRuleType.CUSTOM_DAILY_REL_WEEKLY:
      return {
        type: SkipRuleType.CUSTOM_DAILY_REL_WEEKLY,
        daysRelWeek: parts.slice(1).map((d) => parseInt(d)),
      };
    case SkipRuleType.CUSTOM_DAILY_REL_MONTHLY:
      return {
        type: SkipRuleType.CUSTOM_DAILY_REL_MONTHLY,
        daysRelMonth: parts.slice(1).map((d) => parseInt(d)),
      };
    case SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY:
      return {
        type: SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY,
        weeks: parts.slice(1).map((w) => parseInt(w)),
      };
    case SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY:
      return {
        type: SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY,
        months: parts.slice(1).map((m) => parseInt(m)),
      };
    case SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY:
      return {
        type: SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY,
        quarters: parts.slice(1).map((q) => parseInt(q)),
      };
    default:
      throw new Error(`Unknown skip rule type: ${type}`);
  }
}

export function assembleSkipRule(skipRule: SkipRule): RecurringTaskSkipRule {
  switch (skipRule.type) {
    case SkipRuleType.NONE:
      return "";
    case SkipRuleType.EVEN:
      return SkipRuleType.EVEN;
    case SkipRuleType.ODD:
      return SkipRuleType.ODD;
    case SkipRuleType.EVERY:
      return `${SkipRuleType.EVERY} ${skipRule.n} ${skipRule.k}`;
    case SkipRuleType.CUSTOM_DAILY_REL_WEEKLY: {
      const details = skipRule.daysRelWeek.join(" ");
      return `${SkipRuleType.CUSTOM_DAILY_REL_WEEKLY} ${details}`;
    }
    case SkipRuleType.CUSTOM_DAILY_REL_MONTHLY: {
      const details = skipRule.daysRelMonth.join(" ");
      return `${SkipRuleType.CUSTOM_DAILY_REL_MONTHLY} ${details}`;
    }
    case SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY: {
      const details = skipRule.weeks.join(" ");
      return `${SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY} ${details}`;
    }
    case SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY: {
      const details = skipRule.months.join(" ");
      return `${SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY} ${details}`;
    }
    case SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY: {
      const details = skipRule.quarters.join(" ");
      return `${SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY} ${details}`;
    }
  }
}
