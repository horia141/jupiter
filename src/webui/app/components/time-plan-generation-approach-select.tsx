import { TimePlanGenerationApproach } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";

import { approachName } from "~/logic/domain/time-plan-generation-approach";
import { useBigScreen } from "~/rendering/use-big-screen";

interface TimePlanGenerationApproachSelectProps {
  name: string;
  defaultValue?: TimePlanGenerationApproach;
  value?: TimePlanGenerationApproach;
  onChange?: (newApproach: TimePlanGenerationApproach) => void;
  inputsEnabled: boolean;
}

export function TimePlanGenerationApproachSelect(props: TimePlanGenerationApproachSelectProps) {
  const [approach, setApproach] = useState<TimePlanGenerationApproach>(
    props.defaultValue || props.value || TimePlanGenerationApproach.BOTH_PLAN_AND_TASK
  );
  const isBigScreen = useBigScreen();

  useEffect(() => {
    if (props.value !== undefined) {
      setApproach(props.value);
    }
  }, [props.value]);

  function handleChangeApproach(
    _: React.MouseEvent<HTMLElement>,
    newApproach: TimePlanGenerationApproach | null,
  ) {
    if (newApproach === null) {
      return;
    }
    setApproach(newApproach);
    if (props.onChange) {
      props.onChange(newApproach);
    }
  }

  return (
    <>
      <ToggleButtonGroup
        value={approach}
        exclusive
        fullWidth
        onChange={handleChangeApproach}
      >
        <ToggleButton
          size="small"
          id="approach-both"
          disabled={!props.inputsEnabled}
          value={TimePlanGenerationApproach.BOTH_PLAN_AND_TASK}
        >
          {approachName(TimePlanGenerationApproach.BOTH_PLAN_AND_TASK, !isBigScreen)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="approach-plan"
          disabled={!props.inputsEnabled}
          value={TimePlanGenerationApproach.ONLY_PLAN}
        >
          {approachName(TimePlanGenerationApproach.ONLY_PLAN, !isBigScreen)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="approach-none"
          disabled={!props.inputsEnabled}
          value={TimePlanGenerationApproach.NONE}
        >
          {approachName(TimePlanGenerationApproach.NONE, !isBigScreen)}
        </ToggleButton>
      </ToggleButtonGroup>
      <input name={props.name} type="hidden" value={approach} />
    </>
  );
} 