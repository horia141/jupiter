import { ScheduleSource, ScheduleStream, ScheduleStreamSummary } from "@jupiter/webapi-client";

export function isCorePropertyEditable(scheduleStream: ScheduleStream | ScheduleStreamSummary): boolean {
  return scheduleStream.source === ScheduleSource.USER;
}
