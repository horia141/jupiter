import type { CombinedTimeEventFullDaysEntry } from "~/logic/domain/time-event";
import type { TopLevelInfo } from "~/top-level-context";
import { SectionCard } from "~/components/infra/section-card";
import { TimeEventFullDaysBlockCard } from "~/components/domain/application/calendar/time-event-full-days-block-card";

interface TimeEventFullDaysBlockStackProps {
  topLevelInfo: TopLevelInfo;
  inputsEnabled: boolean;
  title: string;
  entries: CombinedTimeEventFullDaysEntry[];
}

export function TimeEventFullDaysBlockStack(
  props: TimeEventFullDaysBlockStackProps,
) {
  const actions = undefined;

  return (
    <SectionCard
      id="time-event-full-days-block-stack"
      title={props.title}
      actions={actions}
    >
      {props.entries.map((entry) => (
        <TimeEventFullDaysBlockCard
          key={`time-event-full-days-block-${entry.time_event.ref_id}`}
          entry={entry}
        />
      ))}
    </SectionCard>
  );
}
