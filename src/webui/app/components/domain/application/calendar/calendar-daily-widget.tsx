import {
  ADate,
  CalendarEventsEntries,
  CalendarEventsStats,
  Timezone,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import { DateTime } from "luxon";

import { ViewAsCalendarDaily } from "~/components/domain/application/calendar/view-as-calendar-daily";

interface CalendarDailyWidgetProps {
  rightNow: DateTime;
  today: ADate;
  timezone: Timezone;
  period: RecurringTaskPeriod;
  periodStartDate: ADate;
  periodEndDate: ADate;
  entries?: CalendarEventsEntries;
  stats?: CalendarEventsStats;
}

export function CalendarDailyWidget(props: CalendarDailyWidgetProps) {
  return (
    <ViewAsCalendarDaily
      rightNow={props.rightNow}
      today={props.today}
      timezone={props.timezone}
      period={props.period}
      periodStartDate={props.periodStartDate}
      periodEndDate={props.periodEndDate}
      entries={props.entries}
      stats={props.stats}
      calendarLocation={""}
      isAdding={false}
    />
  );
}
