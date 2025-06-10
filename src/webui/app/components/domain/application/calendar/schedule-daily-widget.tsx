import { ViewAsScheduleDailyAndWeekly } from "~/components/domain/application/calendar/view-as-schedule-daily-and-weekly";
import { WidgetProps } from "~/components/domain/application/home/common";

export function ScheduleDailyWidget(props: WidgetProps) {
  const calendar = props.calendar!;
  return (
    <ViewAsScheduleDailyAndWeekly
      rightNow={props.rightNow}
      today={props.today}
      timezone={props.timezone}
      period={calendar.period}
      periodStartDate={calendar.periodStartDate}
      periodEndDate={calendar.periodEndDate}
      entries={calendar.entries}
      calendarLocation={""}
      isAdding={false}
      showOnlyFromRightNowIfDaily
    />
  );
}
