import { HabitRepeatsStrategy } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";
import { strategyName } from "~/logic/domain/habit-repeat-strategy";

interface HabitRepeatStrategySelectProps {
  name: string;
  inputsEnabled: boolean;
  allowNone?: boolean;
  defaultValue?: HabitRepeatsStrategy | "none";
  value?: HabitRepeatsStrategy | "none";
  onChange?: (newStrategy: HabitRepeatsStrategy | "none") => void;
}

export function HabitRepeatStrategySelect(
  props: HabitRepeatStrategySelectProps
) {
  const [strategy, setStrategy] = useState<HabitRepeatsStrategy | "none">(
    props.defaultValue ||
      props.value ||
      (props.allowNone ? "none" : HabitRepeatsStrategy.ALL_SAME)
  );

  useEffect(() => {
    if (props.value !== undefined) {
      setStrategy(props.value);
    }
  }, [props.value]);

  function handleChangeStrategy(
    event: React.MouseEvent<HTMLElement>,
    newStrategy: HabitRepeatsStrategy | "none"
  ) {
    setStrategy(newStrategy);
    if (props.onChange) {
      props.onChange(newStrategy);
    }
  }

  return (
    <>
      <ToggleButtonGroup
        value={strategy || "none"}
        exclusive
        fullWidth
        onChange={handleChangeStrategy}
        sx={{ height: "100%" }}
      >
        {props.allowNone && (
          <ToggleButton value="none" disabled={!props.inputsEnabled}>
            None
          </ToggleButton>
        )}
        {Object.values(HabitRepeatsStrategy).map((s) => (
          <ToggleButton key={s} value={s} disabled={!props.inputsEnabled}>
            {strategyName(s)}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
      <input type="hidden" name={props.name} value={strategy} />
    </>
  );
}
