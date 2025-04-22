import { TimePlanSource } from "@jupiter/webapi-client";

export function timePlanSourceName(source: TimePlanSource): string {
  switch (source) {
    case TimePlanSource.USER:
      return "User";
    case TimePlanSource.GENERATED:
      return "Recurring";
  }
}

export function allowUserChanges(source: TimePlanSource): boolean {
  // Keep synced with python:time-plan-source.py
  return source === TimePlanSource.USER;
}
