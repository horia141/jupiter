import { TextField, Stack } from "@mui/material";
import { HomeTabTarget } from "@jupiter/webapi-client";

interface RowAndColSelectorProps {
  target: HomeTabTarget;
  row: number;
  col: number;
  inputsEnabled?: boolean;
}

export function RowAndColSelector(props: RowAndColSelectorProps) {
  return (
    <Stack direction="row" spacing={2}>
      <TextField
        label="Row"
        type="number"
        name="row"
        value={props.row}
        disabled={!props.inputsEnabled}
        fullWidth
        inputProps={{ min: 0 }}
      />
      <TextField
        label="Column"
        type="number"
        name="col"
        value={props.col}
        disabled={!props.inputsEnabled}
        fullWidth
        inputProps={{ 
          min: 0, 
        }}
      />
    </Stack>
  );
} 