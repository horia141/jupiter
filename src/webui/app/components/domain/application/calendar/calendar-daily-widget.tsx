import { ViewAsCalendarDaily } from "~/components/domain/application/calendar/view-as-calendar-daily";
import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";

export function CalendarDailyWidget(props: WidgetProps) {
  const calendar = props.calendar!;
  return (
    <WidgetContainer>
      <ViewAsCalendarDaily
        rightNow={props.rightNow}
        today={props.today}
        timezone={props.timezone}
        period={calendar.period}
        periodStartDate={calendar.periodStartDate}
        periodEndDate={calendar.periodEndDate}
        entries={calendar.entries}
        calendarLocation={""}
        isAdding={false}
      />
    </WidgetContainer>
  );
}
