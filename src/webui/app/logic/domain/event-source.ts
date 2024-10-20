import { EventSource } from "@jupiter/webapi-client";

export function eventSourceName(source: EventSource) {
  switch (source) {
    case EventSource.CLI:
      return "CLI";
    case EventSource.WEB:
      return "Web";
    case EventSource.SLACK:
      return "Slack";
    case EventSource.EMAIL:
      return "Email";
    case EventSource.GC_CRON:
      return "GC Cron";
    case EventSource.GEN_CRON:
      return "Gen Cron";
  }
}
