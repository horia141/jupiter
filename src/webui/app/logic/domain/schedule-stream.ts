import { ScheduleSource, ScheduleStream } from "@jupiter/webapi-client";

export function isCorePropertyEditable(scheduleStream: ScheduleStream): boolean {
  return scheduleStream.source === ScheduleSource.USER;
}
