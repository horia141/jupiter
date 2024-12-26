import { EventSource } from "@jupiter/webapi-client";

export function eventSourceName(source: EventSource) {
  switch (source) {
    case EventSource.CLI:
      return "Cli";
    case EventSource.WEB:
      return "Web";
    case EventSource.APP:
      return "App";
    case EventSource.GC_CRON:
      return "GC Cron";
    case EventSource.GEN_CRON:
      return "Gen Cron";
    case EventSource.SCHEDULE_EXTERNAL_SYNC_CRON:
      return "Schedule External Sync Cron";
  }
}
