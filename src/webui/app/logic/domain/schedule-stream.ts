import type {
  ScheduleStream,
  ScheduleStreamSummary,
} from "@jupiter/webapi-client";
import { ScheduleSource } from "@jupiter/webapi-client";

export function isCorePropertyEditable(
  scheduleStream: ScheduleStream | ScheduleStreamSummary
): boolean {
  return scheduleStream.source === ScheduleSource.USER;
}
