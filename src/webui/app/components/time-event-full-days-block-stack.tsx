import { Divider, Typography } from "@mui/material";
import type { CombinedTimeEventFullDaysEntry } from "~/logic/domain/time-event";
import { EntityStack } from "./infra/entity-stack";
import { TimeEventFullDaysBlockCard } from "./time-event-full-days-block-card";

interface TimeEventFullDaysBlockStackProps {
  showLabel: boolean;
  label?: string;
  entries: CombinedTimeEventFullDaysEntry[];
}

export function TimeEventFullDaysBlockStack(
  props: TimeEventFullDaysBlockStackProps
) {
  return (
    <EntityStack>
      {props.showLabel && (
        <Divider style={{ paddingTop: "0.5rem" }}>
          <Typography variant="h6">{props.label}</Typography>
        </Divider>
      )}

      {props.entries.map((entry) => (
        <TimeEventFullDaysBlockCard
          key={`time-event-full-days-block-${entry.time_event.ref_id}`}
          entry={entry}
        />
      ))}
    </EntityStack>
  );
}
