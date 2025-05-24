import { HomeTabTarget } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";

import { homeTabTargetName } from "~/logic/domain/home-tab-target";

interface HomeTabTargetSelectProps {
  name: string;
  defaultValue: HomeTabTarget;
  inputsEnabled: boolean;
}

export function HomeTabTargetSelect(props: HomeTabTargetSelectProps) {
  const [target, setTarget] = useState<HomeTabTarget>(props.defaultValue);

  useEffect(() => {
    setTarget(props.defaultValue);
  }, [props.defaultValue]);

  return (
    <>
      <ToggleButtonGroup
        value={target}
        exclusive
        fullWidth
        onChange={(_, newTarget) => newTarget !== null && setTarget(newTarget)}
      >
        <ToggleButton
          size="small"
          id="target-big-screen"
          disabled={!props.inputsEnabled}
          value={HomeTabTarget.BIG_SCREEN}
        >
          {homeTabTargetName(HomeTabTarget.BIG_SCREEN)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="target-small-screen"
          disabled={!props.inputsEnabled}
          value={HomeTabTarget.SMALL_SCREEN}
        >
          {homeTabTargetName(HomeTabTarget.SMALL_SCREEN)}
        </ToggleButton>
      </ToggleButtonGroup>
      <input name={props.name} type="hidden" value={target} />
    </>
  );
}
