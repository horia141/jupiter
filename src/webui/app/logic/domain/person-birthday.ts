import type { PersonBirthday, RecurringTaskDueAtMonth } from "jupiter-gen";

const MONTH_NAME_INDEX = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

export function birthdayFromParts(day: number, month: number): PersonBirthday {
  return `${day} ${MONTH_NAME_INDEX[month]}` as PersonBirthday;
}

export function personBirthdayToStr(personBirthday: PersonBirthday): string {
  return `${personBirthday.day} ${MONTH_NAME_INDEX[personBirthday.month - 1]}`;
}

export function dueMonthToStr(dueMonth: RecurringTaskDueAtMonth): string {
  return MONTH_NAME_INDEX[dueMonth.the_month - 1];
}
