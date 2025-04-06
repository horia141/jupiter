import { RecurringTaskPeriod } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";

import { periodName } from "~/logic/domain/period";
import { useBigScreen } from "~/rendering/use-big-screen";

interface PeriodSelectProps {
  labelId: string;
  label: string;
  name: string;
  allowNonePeriod?: boolean;
  multiSelect?: boolean;
  inputsEnabled: boolean;
  defaultValue?: RecurringTaskPeriod | RecurringTaskPeriod[] | "none";
  value?: RecurringTaskPeriod | RecurringTaskPeriod[] | "none";
  onChange?: (
    newPeriod: RecurringTaskPeriod | RecurringTaskPeriod[] | "none",
  ) => void;
  allowedValues?: RecurringTaskPeriod[];
}

export function PeriodSelect(props: PeriodSelectProps) {
  const isBigScreen = useBigScreen();
  const [period, setPeriod] = useState(
    props.defaultValue ||
      props.value ||
      (props.multiSelect
        ? [RecurringTaskPeriod.DAILY]
        : RecurringTaskPeriod.DAILY),
  );

  useEffect(() => {
    if (props.value !== undefined) {
      if (props.multiSelect) {
        setPeriod(props.value);
      } else {
        setPeriod(props.value);
      }
    }
  }, [props.value, props.multiSelect]);

  function handleChangePeriod(
    event: React.MouseEvent<HTMLElement>,
    newPeriod: RecurringTaskPeriod | RecurringTaskPeriod[] | null,
  ) {
    if (newPeriod === null) {
      return;
    }
    setPeriod(newPeriod);
    if (props.onChange) {
      props.onChange(newPeriod);
    }
  }

  return (
    <>
      <ToggleButtonGroup
        value={period}
        exclusive={!props.multiSelect}
        fullWidth
        onChange={handleChangePeriod}
      >
        {props.allowNonePeriod && (
          <ToggleButton value="none" disabled={!props.inputsEnabled}>
            None
          </ToggleButton>
        )}
        {Object.values(RecurringTaskPeriod)
          .filter(
            (p) => !props.allowedValues || props.allowedValues.includes(p),
          )
          .map((s) => (
            <ToggleButton
              key={s}
              id={`period-${s}`}
              value={s}
              disabled={!props.inputsEnabled}
            >
              {periodName(s, isBigScreen)}
            </ToggleButton>
          ))}
      </ToggleButtonGroup>
      <input type="hidden" name={props.name} value={period} />
    </>
  );
}
