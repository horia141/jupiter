import type { ScheduleEventInDay } from "@jupiter/webapi-client";
import { ScheduleSource } from "@jupiter/webapi-client";

export function isCorePropertyEditable(event: ScheduleEventInDay): boolean {
  return event.source === ScheduleSource.USER;
}
