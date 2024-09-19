import { ScheduleEventInDay, ScheduleSource } from "@jupiter/webapi-client";

export function isCorePropertyEditable(event: ScheduleEventInDay): boolean {
  return event.source === ScheduleSource.USER;
}