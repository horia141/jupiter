import type { ScheduleInDayEventEntry, Timezone } from "@jupiter/webapi-client";
import { TimeEventNamespace } from "@jupiter/webapi-client";
import { type CombinedTimeEventInDayEntry } from "~/logic/domain/time-event";
import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";

interface TimeEventInDayBlockCardProps {
  entry: CombinedTimeEventInDayEntry;
  userTimezone: Timezone;
}

export function TimeEventInDayBlockCard(props: TimeEventInDayBlockCardProps) {
  let name = null;
  switch (props.entry.time_event_in_tz.namespace) {
    case TimeEventNamespace.SCHEDULE_EVENT_IN_DAY: {
      const entry = props.entry.entry as ScheduleInDayEventEntry;
      name = entry.event.name;
      break;
    }

    case TimeEventNamespace.INBOX_TASK: {
      name = `On ${props.entry.time_event_in_tz.start_date} at ${props.entry.time_event_in_tz.start_time_in_day}`;
      break;
    }

    default:
      throw new Error("Unknown namespace");
  }

  return (
    <EntityCard
      entityId={`time-event-in-day-block-${props.entry.time_event_in_tz.ref_id}`}
      showAsArchived={props.entry.time_event_in_tz.archived}
    >
      <EntityLink
        to={`/workspace/calendar/time-event/in-day-block/${props.entry.time_event_in_tz.ref_id}`}
      >
        <EntityNameComponent name={name} />
      </EntityLink>
    </EntityCard>
  );
}
