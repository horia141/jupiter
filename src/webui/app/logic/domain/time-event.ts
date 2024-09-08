import type {
  InboxTaskEntry,
  Person,
  PersonEntry,
  ScheduleFullDaysEventEntry,
  ScheduleInDayEventEntry,
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
} from "@jupiter/webapi-client";
import { ScheduleStreamColor } from "@jupiter/webapi-client";
import { aDateToDate, compareADate } from "./adate";

export function birthdayTimeEventName(
  block: TimeEventFullDaysBlock,
  person: Person
) {
  const date = aDateToDate(block.start_date);
  return `${person.name}'s Birthday '${date.toFormat("yy")}`;
}

export const BIRTHDAY_TIME_EVENT_COLOR = ScheduleStreamColor.GREEN;

export function sortBirthdayTimeEventsNaturally(
  timeEvents: Array<CombinedTimeEventFullDaysEntry>
): CombinedTimeEventFullDaysEntry[] {
  return [...timeEvents].sort((j1, j2) => {
    return compareADate(j1.time_event.start_date, j2.time_event.start_date);
  });
}
export interface CombinedTimeEventFullDaysEntry {
  time_event: TimeEventFullDaysBlock;
  entry: ScheduleFullDaysEventEntry | PersonEntry;
}
export interface CombinedTimeEventInDayEntry {
  time_event: TimeEventInDayBlock;
  entry: ScheduleInDayEventEntry | InboxTaskEntry;
}
