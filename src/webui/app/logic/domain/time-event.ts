import type {
  InboxTaskEntry,
  Person,
  PersonEntry,
  ScheduleFullDaysEventEntry,
  ScheduleInDayEventEntry,
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
  VacationEntry,
} from "@jupiter/webapi-client";
import {
  ScheduleStreamColor,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import { aDateToDate, compareADate } from "./adate";

export function birthdayTimeEventName(
  block: TimeEventFullDaysBlock,
  person: Person
) {
  const date = aDateToDate(block.start_date);
  return `${person.name}'s Birthday '${date.toFormat("yy")}`;
}

export const BIRTHDAY_TIME_EVENT_COLOR = ScheduleStreamColor.GREEN;
export const VACATION_TIME_EVENT_COLOR = ScheduleStreamColor.BLUE;

export function sortBirthdayTimeEventsNaturally(
  timeEvents: Array<CombinedTimeEventFullDaysEntry>
): CombinedTimeEventFullDaysEntry[] {
  return [...timeEvents].sort((j1, j2) => {
    return compareADate(j1.time_event.start_date, j2.time_event.start_date);
  });
}
export interface CombinedTimeEventFullDaysEntry {
  time_event: TimeEventFullDaysBlock;
  entry: ScheduleFullDaysEventEntry | PersonEntry | VacationEntry;
}
export interface CombinedTimeEventInDayEntry {
  time_event: TimeEventInDayBlock;
  entry: ScheduleInDayEventEntry | InboxTaskEntry;
}

const FULL_DaYS_TIME_EVENT_NAMESPACES_IN_ORDER = [
  TimeEventNamespace.VACATION,
  TimeEventNamespace.PERSON_BIRTHDAY,
  TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK,
];

export function compareNamespaceForSortingFullDaysTimeEvents(
  namespace1: TimeEventNamespace,
  namespace2: TimeEventNamespace
): number {
  const index1 = FULL_DaYS_TIME_EVENT_NAMESPACES_IN_ORDER.indexOf(namespace1);
  const index2 = FULL_DaYS_TIME_EVENT_NAMESPACES_IN_ORDER.indexOf(namespace2);

  return index1 - index2;
}
