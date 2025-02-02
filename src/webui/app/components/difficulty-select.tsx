import { Difficulty } from "@jupiter/webapi-client";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useEffect, useState } from "react";
import { difficultyName } from "~/logic/domain/difficulty";

interface DifficultySelectProps {
  name: string;
  defaultValue: Difficulty;
  inputsEnabled: boolean;
}

export function DifficultySelect(props: DifficultySelectProps) {
  const [difficulty, setDifficulty] = useState<Difficulty>(props.defaultValue);

  useEffect(() => {
    setDifficulty(props.defaultValue);
  }, [props.defaultValue]);

  return (
    <>
      <ToggleButtonGroup
        value={difficulty}
        exclusive
        fullWidth
        onChange={(_, newDifficulty) =>
          newDifficulty !== null && setDifficulty(newDifficulty)
        }
      >
        <ToggleButton
          size="small"
          id="difficulty-easy"
          disabled={!props.inputsEnabled}
          value={Difficulty.EASY}
        >
          {difficultyName(Difficulty.EASY)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="difficulty-medium"
          disabled={!props.inputsEnabled}
          value={Difficulty.MEDIUM}
        >
          {difficultyName(Difficulty.MEDIUM)}
        </ToggleButton>
        <ToggleButton
          size="small"
          id="difficulty-hard"
          disabled={!props.inputsEnabled}
          value={Difficulty.HARD}
        >
          {difficultyName(Difficulty.HARD)}
        </ToggleButton>
      </ToggleButtonGroup>
      <input name={props.name} type="hidden" value={difficulty} />
    </>
  );
}
