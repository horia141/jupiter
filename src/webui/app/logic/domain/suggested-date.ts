import { ADate, BigPlan, TimePlan } from "@jupiter/webapi-client";

import { aDateToDate, dateToAdate } from "~/logic/domain/adate";

export interface SuggestedDate {
  date: ADate;
  label: string;
}

export function getSuggestedDatesForInboxTaskActionableDate(
  today: ADate,
  bigPlan?: BigPlan | null,
  timePlan?: TimePlan | null,
): SuggestedDate[] {
  const todayDate = aDateToDate(today);
  const suggestedDates: SuggestedDate[] = [
    {
      date: today,
      label: "Today",
    },
    {
      date: dateToAdate(todayDate.plus({ days: 7 }).startOf("week")),
      label: "Start of the next week",
    },
    {
      date: dateToAdate(todayDate.plus({ months: 1 }).startOf("month")),
      label: "Start of the next month",
    },
  ];

  if (bigPlan && bigPlan.actionable_date) {
    suggestedDates.push({
      date: bigPlan.actionable_date,
      label: "Parent big plan actionable date",
    });
  }

  if (timePlan) {
    suggestedDates.push({
      date: timePlan.start_date,
      label: "Associated time plan start date",
    });
  }

  return suggestedDates;
}

export function getSuggestedDatesForInboxTaskDueDate(
  today: ADate,
  bigPlan?: BigPlan | null,
  timePlan?: TimePlan | null,
): SuggestedDate[] {
  const todayDate = aDateToDate(today);
  const suggestedDates: SuggestedDate[] = [
    {
      date: today,
      label: "Today",
    },
    {
      date: dateToAdate(todayDate.plus({ days: 1 }).endOf("week")),
      label: "End of the week",
    },
    {
      date: dateToAdate(todayDate.plus({ days: 1 }).endOf("month")),
      label: "End of the month",
    },
  ];

  if (bigPlan && bigPlan.due_date) {
    suggestedDates.push({
      date: bigPlan.due_date,
      label: "Parent big plan due date",
    });
  }

  if (timePlan) {
    suggestedDates.push({
      date: timePlan.end_date,
      label: "Associated time plan end date",
    });
  }

  return suggestedDates;
}

export function getSuggestedDatesForBigPlanActionableDate(
  today: ADate,
  timePlan?: TimePlan | null,
): SuggestedDate[] {
  const todayDate = aDateToDate(today);
  const suggestedDates: SuggestedDate[] = [
    {
      date: today,
      label: "Today",
    },
    {
      date: dateToAdate(todayDate.plus({ months: 1 }).startOf("month")),
      label: "Start of the next month",
    },
    {
      date: dateToAdate(todayDate.plus({ months: 3 }).startOf("quarter")),
      label: "Start of the next quarter",
    },
  ];

  if (timePlan) {
    suggestedDates.push({
      date: timePlan.start_date,
      label: "Associated time plan start date",
    });
  }

  return suggestedDates;
}

export function getSuggestedDatesForBigPlanDueDate(
  today: ADate,
  timePlan?: TimePlan | null,
): SuggestedDate[] {
  const todayDate = aDateToDate(today);
  const suggestedDates: SuggestedDate[] = [
    {
      date: today,
      label: "Today",
    },
    {
      date: dateToAdate(todayDate.plus({ days: 1 }).endOf("month")),
      label: "End of the month",
    },
    {
      date: dateToAdate(todayDate.plus({ days: 1 }).endOf("quarter")),
      label: "End of the quarter",
    },
    {
      date: dateToAdate(todayDate.plus({ days: 1 }).endOf("year")),
      label: "End of the year",
    },
  ];

  if (timePlan) {
    suggestedDates.push({
      date: timePlan.end_date,
      label: "Associated time plan end date",
    });
  }

  return suggestedDates;
}

export function getSuggestedDatesForBigPlanMilestoneDate(
  today: ADate,
): SuggestedDate[] {
  return getSuggestedDatesForBigPlanDueDate(today, timePlan);
}
