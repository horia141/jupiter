import type { Person } from "@jupiter/webapi-client";
import { ScheduleStreamColor } from "@jupiter/webapi-client";

export function birthdayTimeEventName(person: Person) {
  return `${person.name}'s Birthday`;
}

export const BIRTHDAY_TIME_EVENT_COLOR = ScheduleStreamColor.GREEN;
