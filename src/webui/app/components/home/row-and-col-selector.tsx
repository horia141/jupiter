import { TextField, Stack } from "@mui/material";
import { HomeTabTarget } from "@jupiter/webapi-client";
import { constructFieldName } from "~/logic/field-names";

interface RowAndColSelectorProps {
  namePrefix: string;
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
        name={constructFieldName(props.namePrefix, "row")}
        value={props.row}
        disabled={!props.inputsEnabled}
        fullWidth
        inputProps={{ min: 0 }}
      />
      <TextField
        label="Column"
        type="number"
        name={constructFieldName(props.namePrefix, "col")}
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