import { TimePlanActivityFeasability } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";
import { timePlanActivityFeasabilityName } from "~/logic/domain/time-plan-activity-feasability";

interface TimePlanActivityFeasabilitySelectProps {
  name: string;
  defaultValue: TimePlanActivityFeasability;
  inputsEnabled: boolean;
}

export function TimePlanActivityFeasabilitySelect(
  props: TimePlanActivityFeasabilitySelectProps
) {
  const [feasability, setFeasability] = useState<TimePlanActivityFeasability>(
    props.defaultValue
  );

  useEffect(() => {
    setFeasability(props.defaultValue);
  }, [props.defaultValue]);

  return (
    <>
      <ToggleButtonGroup
        size="small"
        fullWidth
        value={feasability}
        exclusive
        onChange={(_, newFeasability) =>
          newFeasability !== null && setFeasability(newFeasability)
        }
        sx={{ height: "100%" }}
      >
        <ToggleButton
          id="time-plan-activity-feasability-must-do"
          disabled={!props.inputsEnabled}
          value={TimePlanActivityFeasability.MUST_DO}
        >
          {timePlanActivityFeasabilityName(TimePlanActivityFeasability.MUST_DO)}
        </ToggleButton>
        <ToggleButton
          id="time-plan-activity-feasability-nice-to-have"
          disabled={!props.inputsEnabled}
          value={TimePlanActivityFeasability.NICE_TO_HAVE}
        >
          {timePlanActivityFeasabilityName(
            TimePlanActivityFeasability.NICE_TO_HAVE
          )}
        </ToggleButton>
        <ToggleButton
          id="time-plan-activity-feasability-stretch"
          disabled={!props.inputsEnabled}
          value={TimePlanActivityFeasability.STRETCH}
        >
          {timePlanActivityFeasabilityName(TimePlanActivityFeasability.STRETCH)}
        </ToggleButton>
      </ToggleButtonGroup>
      <input name={props.name} type="hidden" value={feasability} />
    </>
  );
}
