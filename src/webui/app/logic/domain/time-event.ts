import type {
  ADate,
  InboxTaskEntry,
  Person,
  PersonEntry,
  ScheduleFullDaysEventEntry,
  ScheduleInDayEventEntry,
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
  TimeInDay,
  Timezone,
  VacationEntry,
} from "@jupiter/webapi-client";
import {
  ScheduleStreamColor,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import { DateTime } from "luxon";

import { computeTimeEventInDayDurationInQuarters } from "~/routes/app/workspace/calendar";

import { aDateToDate, compareADate } from "./adate";

export function birthdayTimeEventName(
  block: TimeEventFullDaysBlock,
  person: Person,
) {
  const date = aDateToDate(block.start_date);
  return `${person.name}'s Birthday '${date.toFormat("yy")}`;
}

export const INBOX_TASK_TIME_EVENT_COLOR = ScheduleStreamColor.BLUE;
export const BIRTHDAY_TIME_EVENT_COLOR = ScheduleStreamColor.GREEN;
export const VACATION_TIME_EVENT_COLOR = ScheduleStreamColor.ORANGE;

export function sortBirthdayTimeEventsNaturally(
  timeEvents: Array<CombinedTimeEventFullDaysEntry>,
): CombinedTimeEventFullDaysEntry[] {
  return [...timeEvents].sort((j1, j2) => {
    return compareADate(j1.time_event.start_date, j2.time_event.start_date);
  });
}

export function sortInboxTaskTimeEventsNaturally(
  timeEvents: Array<CombinedTimeEventInDayEntry>,
): CombinedTimeEventInDayEntry[] {
  return [...timeEvents].sort((j1, j2) => {
    return (
      calculateStartTimeForTimeEvent(j1.time_event_in_tz).toMillis() -
      calculateStartTimeForTimeEvent(j2.time_event_in_tz).toMillis()
    );
  });
}

export interface CombinedTimeEventFullDaysEntry {
  time_event: TimeEventFullDaysBlock;
  entry: ScheduleFullDaysEventEntry | PersonEntry | VacationEntry;
}

export interface CombinedTimeEventInDayEntry {
  time_event_in_tz: TimeEventInDayBlock;
  entry: ScheduleInDayEventEntry | InboxTaskEntry;
}

const FULL_DaYS_TIME_EVENT_NAMESPACES_IN_ORDER = [
  TimeEventNamespace.VACATION,
  TimeEventNamespace.PERSON_BIRTHDAY,
  TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK,
];

export function compareNamespaceForSortingFullDaysTimeEvents(
  namespace1: TimeEventNamespace,
  namespace2: TimeEventNamespace,
): number {
  const index1 = FULL_DaYS_TIME_EVENT_NAMESPACES_IN_ORDER.indexOf(namespace1);
  const index2 = FULL_DaYS_TIME_EVENT_NAMESPACES_IN_ORDER.indexOf(namespace2);

  return index1 - index2;
}

export function isTimeEventInDayBlockEditable(namespace: TimeEventNamespace) {
  if (namespace === TimeEventNamespace.INBOX_TASK) {
    return true;
  }

  return false;
}

interface TimeEventInDayBlockParams {
  startDate: ADate;
  startTimeInDay?: TimeInDay;
}

export function calculateStartTimeFromBlockParams(
  blockParams: TimeEventInDayBlockParams,
): DateTime {
  return DateTime.fromISO(
    `${blockParams.startDate}T${blockParams.startTimeInDay}`,
    { zone: "UTC" },
  );
}

export function calculateEndTimeFromBlockParams(
  blockParams: TimeEventInDayBlockParams,
  durationMins: number,
): DateTime<true> {
  const startTime = calculateStartTimeFromBlockParams(blockParams);
  return startTime.plus({ minutes: durationMins });
}

export function calculateStartTimeForTimeEvent(
  timeEvent: TimeEventInDayBlock,
): DateTime<true> {
  const startTime = DateTime.fromISO(
    `${timeEvent.start_date}T${timeEvent.start_time_in_day}`,
    { zone: "UTC" },
  );
  if (!startTime.isValid) {
    throw new Error(
      `Invalid start time: ${timeEvent.start_date}T${timeEvent.start_time_in_day}`,
    );
  }
  return startTime;
}

export function calculateEndTimeForTimeEvent(
  timeEvent: TimeEventInDayBlock,
): DateTime<true> {
  const startTime = calculateStartTimeForTimeEvent(timeEvent);
  const endTime = startTime.plus({ minutes: timeEvent.duration_mins });

  return endTime;
}

export function timeEventInDayBlockToTimezone(
  timeEvent: TimeEventInDayBlock,
  timezone: Timezone,
): TimeEventInDayBlock {
  const { startDate, startTimeInDay } = timeEventInDayBlockParamsToTimezone(
    {
      startDate: timeEvent.start_date,
      startTimeInDay: timeEvent.start_time_in_day,
    },
    timezone,
  );

  return {
    ...timeEvent,
    start_date: startDate,
    start_time_in_day: startTimeInDay!,
  };
}

export function timeEventInDayBlockParamsToUtc(
  params: TimeEventInDayBlockParams,
  timezone: Timezone,
): TimeEventInDayBlockParams {
  if (!params.startTimeInDay) {
    // This works around some issues in the uI where the control for
    // time in day can be null which needs to trigger a validation error
    // from the backend.
    return params;
  }
  const startTime = DateTime.fromISO(
    `${params.startDate}T${params.startTimeInDay}`,
    { zone: timezone },
  );
  if (!startTime.isValid) {
    throw new Error(
      `Invalid start time: ${params.startDate}T${params.startTimeInDay}`,
    );
  }
  const utcStartTime = startTime.toUTC();
  return {
    startDate: utcStartTime.toISODate(),
    startTimeInDay: utcStartTime.toFormat("HH:mm"),
  };
}

export function timeEventInDayBlockParamsToTimezone(
  params: TimeEventInDayBlockParams,
  timezone: Timezone,
): TimeEventInDayBlockParams {
  if (!params.startTimeInDay) {
    // This works around some issues in the uI where the control for
    // time in day can be null which needs to trigger a validation error
    // from the backend.
    return params;
  }
  const startTime = DateTime.fromISO(
    `${params.startDate}T${params.startTimeInDay}`,
    { zone: "UTC" },
  );
  if (!startTime.isValid) {
    throw new Error(
      `Invalid start time: ${params.startDate}T${params.startTimeInDay}`,
    );
  }
  const localStartTime = startTime.setZone(timezone);
  if (!localStartTime.isValid) {
    throw new Error(
      `Invalid start time: ${params.startDate}T${params.startTimeInDay}`,
    );
  }
  return {
    startDate: localStartTime.toISODate(),
    startTimeInDay: localStartTime.toFormat("HH:mm"),
  };
}

export function calendarTimeEventInDayStartMinutesToRems(
  startMins: number,
): string {
  // Each 15 minutes is 1 rem. Display has 96=4*24 rem height.
  const startHours = Math.max(0, startMins / 15);
  return `${startHours}rem`;
}

export function calendarPxHeightToMinutes(
  pxHeight: number,
  remHeight: number,
): number {
  return Math.floor(pxHeight / remHeight) * 15;
}

export function calendarTimeEventInDayDurationToRems(
  minutesSinceStartOfDay: number,
  durationMins: number,
): string {
  const durationInQuarters = computeTimeEventInDayDurationInQuarters(
    minutesSinceStartOfDay,
    durationMins,
  );
  return `${durationInQuarters}rem`;
}

export function scheduleTimeEventInDayDurationToRems(
  durationMins: number,
): string {
  const durationInHalfs = 0.5 + Math.floor(durationMins / 30);
  return `${durationInHalfs}rem`;
}
