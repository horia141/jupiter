import type { CombinedTimeEventInDayEntry } from "~/logic/domain/time-event";
import type { TopLevelInfo } from "~/top-level-context";

import { NavSingle, SectionActions } from "./infra/section-actions";
import { SectionCardNew } from "./infra/section-card-new";
import { TimeEventInDayBlockCard } from "./time-event-in-day-block-card";

interface TimeEventInDayBlockStackProps {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  title: string;
  createLocation?: string;
  entries: CombinedTimeEventInDayEntry[];
}

export function TimeEventInDayBlockStack(props: TimeEventInDayBlockStackProps) {
  let actions = undefined;
  if (props.createLocation) {
    actions = (
      <SectionActions
        id="time-event-in-day-block-stack"
        topLevelInfo={props.topLevelInfo}
        inputsEnabled={props.inputsEnabled}
        actions={[
          NavSingle({
            text: "Add",
            link: props.createLocation,
            highlight: true,
          }),
        ]}
      />
    );
  }

  return (
    <SectionCardNew
      id="time-event-in-day-block-stack"
      title={props.title}
      actions={actions}
    >
      {props.entries.map((entry) => (
        <TimeEventInDayBlockCard
          key={`time-event-in-days-block-${entry.time_event_in_tz.ref_id}`}
          entry={entry}
          userTimezone={props.topLevelInfo.user.timezone}
        />
      ))}
    </SectionCardNew>
  );
}
