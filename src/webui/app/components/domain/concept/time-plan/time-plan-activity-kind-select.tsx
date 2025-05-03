import { TimePlanActivityKind } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";

import { timePlanActivityKindName } from "~/logic/domain/time-plan-activity-kind";

interface TimePlanActivityKindSelectProps {
  name: string;
  defaultValue: TimePlanActivityKind;
  inputsEnabled: boolean;
}

export function TimePlanActivitKindSelect(
  props: TimePlanActivityKindSelectProps,
) {
  const [kind, setKind] = useState<TimePlanActivityKind>(props.defaultValue);

  useEffect(() => {
    setKind(props.defaultValue);
  }, [props.defaultValue]);

  return (
    <>
      <ToggleButtonGroup
        size="small"
        fullWidth
        value={kind}
        exclusive
        onChange={(_, newKind) => newKind !== null && setKind(newKind)}
        sx={{ height: "100%" }}
      >
        <ToggleButton
          id="time-plan-activity-kind-finish"
          disabled={!props.inputsEnabled}
          value={TimePlanActivityKind.FINISH}
        >
          {timePlanActivityKindName(TimePlanActivityKind.FINISH)}
        </ToggleButton>
        <ToggleButton
          id="time-plan-activity-kind-make-progress"
          disabled={!props.inputsEnabled}
          value={TimePlanActivityKind.MAKE_PROGRESS}
        >
          {timePlanActivityKindName(TimePlanActivityKind.MAKE_PROGRESS)}
        </ToggleButton>
      </ToggleButtonGroup>
      <input name={props.name} type="hidden" value={kind} />
    </>
  );
}
