import {
  ADate,
  EntityId,
  InboxTaskEntry,
  Person,
  PersonEntry,
  RecurringTaskPeriod,
  ScheduleFullDaysEventEntry,
  ScheduleInDayEventEntry,
  TimeEventFullDaysBlock,
  TimeEventInDayBlock,
  TimeInDay,
  Timezone,
  VacationEntry,
  ScheduleStreamColor,
  TimeEventNamespace,
} from "@jupiter/webapi-client";
import { DateTime } from "luxon";

import { measureText } from "~/utils";
import { aDateToDate, compareADate } from "~/logic/domain/adate";

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

export function computeTimeEventInDayDurationInQuarters(
  minutesSinceStartOfDay: number,
  durationMins: number,
): number {
  // Each 15 minutes is 1 rem. Display has 96=4*24 rem height.
  // If the event goes beyond the day, we cap it at 24 hours.
  const finalOffsetInMinutes = minutesSinceStartOfDay + durationMins;
  let finalDurationInMins = durationMins;
  if (finalOffsetInMinutes > 24 * 60) {
    finalDurationInMins = Math.max(15, 24 * 60 - minutesSinceStartOfDay);
  }
  return Math.max(1, finalDurationInMins / 15);
}

export function clipTimeEventFullDaysNameToWhatFits(
  name: string,
  fontSize: number,
  containerWidth: number,
): string {
  const textWidthInPx = measureText(name, fontSize);

  if (textWidthInPx <= containerWidth) {
    return name;
  } else {
    // Do some rough approximation here.
    const maxChars = Math.floor((name.length * containerWidth) / textWidthInPx);
    return `${name.substring(0, maxChars)} ...`;
  }
}

export function clipTimeEventInDayNameToWhatFits(
  startTime: DateTime,
  endTime: DateTime,
  name: string,
  fontSize: number,
  containerWidth: number,
  minutesSinceStartOfDay: number,
  durationInMins: number,
): string {
  const durationInQuarters = computeTimeEventInDayDurationInQuarters(
    0,
    durationInMins,
  );
  const durationInHalfs = Math.max(1, Math.floor(durationInQuarters / 2));

  const bigName = `[${startTime.toFormat("HH:mm")} - ${endTime.toFormat(
    "HH:mm",
  )}] ${name}`;
  const textWidthInPx = measureText(bigName, fontSize);
  const totalWidthInPx = containerWidth * durationInHalfs;

  if (textWidthInPx <= totalWidthInPx) {
    return bigName;
  } else {
    // Do some rough approximation here.
    const maxChars = Math.max(
      3,
      Math.floor((name.length * totalWidthInPx) / textWidthInPx),
    );
    return `[${startTime.toFormat("HH:mm")}] ${name.substring(
      0,
      maxChars,
    )} ...`;
  }
}

export function combinedTimeEventFullDayEntryPartionByDay(
  entries: Array<CombinedTimeEventFullDaysEntry>,
): Record<string, Array<CombinedTimeEventFullDaysEntry>> {
  const partition: Record<string, Array<CombinedTimeEventFullDaysEntry>> = {};

  for (const entry of entries) {
    const firstDate = aDateToDate(entry.time_event.start_date);
    for (let idx = 0; idx < entry.time_event.duration_days; idx++) {
      const date = firstDate.plus({ days: idx });

      const dateStr = date.toISODate();
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(entry);
    }
  }

  for (const dateStr in partition) {
    partition[dateStr] = sortTimeEventFullDaysByType(partition[dateStr]);
  }

  return partition;
}

export function sortTimeEventFullDaysByType(
  entries: Array<CombinedTimeEventFullDaysEntry>,
) {
  return entries.sort((a, b) => {
    if (a.time_event.namespace === b.time_event.namespace) {
      return compareADate(a.time_event.start_date, b.time_event.start_date);
    }

    return compareNamespaceForSortingFullDaysTimeEvents(
      a.time_event.namespace,
      b.time_event.namespace,
    );
  });
}

export function splitTimeEventInDayEntryIntoPerDayEntries(
  entry: CombinedTimeEventInDayEntry,
): {
  day1: CombinedTimeEventInDayEntry;
  day2?: CombinedTimeEventInDayEntry;
  day3?: CombinedTimeEventInDayEntry;
} {
  const startTime = calculateStartTimeForTimeEvent(entry.time_event_in_tz);
  const endTime = calculateEndTimeForTimeEvent(entry.time_event_in_tz);
  const diffInDays = endTime
    .startOf("day")
    .diff(startTime.startOf("day"), "days").days;

  if (diffInDays === 0) {
    // Here we have only one day.
    return {
      day1: entry,
    };
  } else if (diffInDays === 1) {
    // Here we have two days.
    const day1TimeEvent = {
      ...entry.time_event_in_tz,
      duration_mins:
        -1 *
        startTime.diff(startTime.set({ hour: 23, minute: 59 })).as("minutes"),
    };
    const day2TimeEvent = {
      ...entry.time_event_in_tz,
      start_date: endTime.toISODate(),
      start_time_in_day: "00:00",
      duration_mins: endTime
        .diff(endTime.set({ hour: 0, minute: 0 }))
        .as("minutes"),
    };

    return {
      day1: {
        time_event_in_tz: day1TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day1TimeEvent,
        },
      },
      day2: {
        time_event_in_tz: day2TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day2TimeEvent,
        },
      },
    };
  } else if (diffInDays === 2) {
    // Here we have three days.
    const day1TimeEvent = {
      ...entry.time_event_in_tz,
      duration_mins:
        -1 *
        startTime.diff(startTime.set({ hour: 23, minute: 59 })).as("minutes"),
    };
    const day2TimeEvent = {
      ...entry.time_event_in_tz,
      start_date: startTime.plus({ days: 1 }).toISODate(),
      start_time_in_day: "00:00",
      duration_mins: 24 * 60,
    };
    const day3TimeEvent = {
      ...entry.time_event_in_tz,
      start_date: endTime.toISODate(),
      start_time_in_day: "00:00",
      duration_mins: endTime
        .diff(endTime.set({ hour: 0, minute: 0 }))
        .as("minutes"),
    };

    return {
      day1: {
        time_event_in_tz: day1TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day1TimeEvent,
        },
      },
      day2: {
        time_event_in_tz: day2TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day2TimeEvent,
        },
      },
      day3: {
        time_event_in_tz: day3TimeEvent,
        entry: {
          ...entry.entry,
          time_event: day3TimeEvent,
        },
      },
    };
  } else {
    throw new Error("Unexpected time event duration");
  }
}

export function combinedTimeEventInDayEntryPartionByDay(
  entries: Array<CombinedTimeEventInDayEntry>,
): Record<string, Array<CombinedTimeEventInDayEntry>> {
  const partition: Record<string, Array<CombinedTimeEventInDayEntry>> = {};

  for (const entry of entries) {
    const splitEntries = splitTimeEventInDayEntryIntoPerDayEntries(entry);

    const dateStr = splitEntries.day1.time_event_in_tz.start_date;
    if (partition[dateStr] === undefined) {
      partition[dateStr] = [];
    }
    partition[dateStr].push(splitEntries.day1);

    if (splitEntries.day2) {
      const dateStr = splitEntries.day2.time_event_in_tz.start_date;
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(splitEntries.day2);
    }

    if (splitEntries.day3) {
      const dateStr = splitEntries.day3.time_event_in_tz.start_date;
      if (partition[dateStr] === undefined) {
        partition[dateStr] = [];
      }
      partition[dateStr].push(splitEntries.day3);
    }
  }

  // Now sort all partitions.
  for (const dateStr in partition) {
    partition[dateStr] = sortTimeEventInDayByStartTimeAndEndTime(
      partition[dateStr],
    );
  }

  return partition;
}

export function sortTimeEventInDayByStartTimeAndEndTime(
  entries: Array<CombinedTimeEventInDayEntry>,
) {
  return entries.sort((a, b) => {
    const aStartTime = calculateStartTimeForTimeEvent(a.time_event_in_tz);
    const bStartTime = calculateStartTimeForTimeEvent(b.time_event_in_tz);

    if (aStartTime === bStartTime) {
      const aEndTime = calculateEndTimeForTimeEvent(a.time_event_in_tz);
      const bEndTime = calculateEndTimeForTimeEvent(b.time_event_in_tz);
      return aEndTime < bEndTime ? -1 : 1;
    }
    return aStartTime < bStartTime ? -1 : 1;
  });
}

export function buildTimeBlockOffsetsMap(
  entries: Array<CombinedTimeEventInDayEntry>,
  startOfDay: DateTime,
): Map<EntityId, number> {
  const offsets = new Map<EntityId, number>();

  const freeOffsetsMap = [];
  for (let idx = 0; idx < 24 * 4; idx++) {
    freeOffsetsMap.push({
      time: startOfDay.plus({ minutes: idx * 15 }),
      offset0: false,
      offset1: false,
      offset2: false,
      offset3: false,
      offset4: false,
    });
  }

  for (const entry of entries) {
    const startTime = calculateStartTimeForTimeEvent(entry.time_event_in_tz);
    const minutesSinceStartOfDay = startTime.diff(startOfDay).as("minutes");

    const firstCellIdx = Math.floor(minutesSinceStartOfDay / 15);
    const offsetCell = freeOffsetsMap[firstCellIdx];

    if (offsetCell.offset0 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 0);
      offsetCell.offset0 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset0 = true;
      }
      continue;
    } else if (offsetCell.offset1 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 1);
      offsetCell.offset1 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset1 = true;
      }
      continue;
    } else if (offsetCell.offset2 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 2);
      offsetCell.offset2 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset2 = true;
      }
      continue;
    } else if (offsetCell.offset3 === false) {
      offsets.set(entry.time_event_in_tz.ref_id, 3);
      offsetCell.offset3 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset3 = true;
      }
      continue;
    } else {
      offsets.set(entry.time_event_in_tz.ref_id, 4);
      offsetCell.offset4 = true;
      for (
        let idx = minutesSinceStartOfDay;
        idx < minutesSinceStartOfDay + entry.time_event_in_tz.duration_mins;
        idx += 15
      ) {
        freeOffsetsMap[Math.floor(idx / 15)].offset4 = true;
      }
      continue;
    }
  }

  return offsets;
}

export function statsSubperiodForPeriod(
  period: RecurringTaskPeriod,
): RecurringTaskPeriod | null {
  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return null;
    case RecurringTaskPeriod.WEEKLY:
      return RecurringTaskPeriod.DAILY;
    case RecurringTaskPeriod.MONTHLY:
      return RecurringTaskPeriod.DAILY;
    case RecurringTaskPeriod.QUARTERLY:
      return RecurringTaskPeriod.WEEKLY;
    case RecurringTaskPeriod.YEARLY:
      return RecurringTaskPeriod.MONTHLY;
  }
}

export function monthToQuarter(month: number): string {
  switch (month) {
    case 1:
    case 2:
    case 3:
      return "Q1";
    case 4:
    case 5:
    case 6:
      return "Q2";
    case 7:
    case 8:
    case 9:
      return "Q3";
    case 10:
    case 11:
    case 12:
      return "Q4";
    default:
      throw new Error("Unexpected month");
  }
}
