import { Eisen } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";
import { eisenName } from "~/logic/domain/eisen";
import { useBigScreen } from "~/rendering/use-big-screen";

interface EisenhowerSelectProps {
  name: string;
  defaultValue: Eisen;
  inputsEnabled: boolean;
}

export function EisenhowerSelect(props: EisenhowerSelectProps) {
  const [eisen, setEisen] = useState<Eisen>(props.defaultValue);
  const isBigScreen = useBigScreen();

  useEffect(() => {
    setEisen(props.defaultValue);
  }, [props.defaultValue]);

  return (
    <>
      <ToggleButtonGroup
        value={eisen}
        exclusive
        fullWidth
        onChange={(_, newEisen) => newEisen !== null && setEisen(newEisen)}
      >
        <ToggleButton
          size="small"
          id="eisen-regular"
          disabled={!props.inputsEnabled}
          value={Eisen.REGULAR}
        >
          {eisenName(Eisen.REGULAR, !isBigScreen)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="eisen-important"
          disabled={!props.inputsEnabled}
          value={Eisen.IMPORTANT}
        >
          {eisenName(Eisen.IMPORTANT, !isBigScreen)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="eisen-urgent"
          disabled={!props.inputsEnabled}
          value={Eisen.URGENT}
        >
          {eisenName(Eisen.URGENT, !isBigScreen)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="eisen-important-and-urgent"
          disabled={!props.inputsEnabled}
          value={Eisen.IMPORTANT_AND_URGENT}
        >
          {eisenName(Eisen.IMPORTANT_AND_URGENT, !isBigScreen)}
        </ToggleButton>
      </ToggleButtonGroup>
      <input name={props.name} type="hidden" value={eisen} />
    </>
  );
}
