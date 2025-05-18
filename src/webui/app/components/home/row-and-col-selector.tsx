import { TextField, Stack } from "@mui/material";
import { HomeTabTarget } from "@jupiter/webapi-client";
import { constructFieldName } from "~/logic/field-names";
import { useEffect, useState } from "react";

interface RowAndColSelectorProps {
  namePrefix: string;
  target: HomeTabTarget;
  row: number;
  col: number;
  onRowAndColChange?: (row: number, col: number) => void;
  inputsEnabled?: boolean;
}

export function RowAndColSelector(props: RowAndColSelectorProps) {
  const [row, setRow] = useState(props.row);
  const [col, setCol] = useState(props.col);

  useEffect(() => {
    setRow(props.row);
    setCol(props.col);
  }, [props.row, props.col]);

  return (
    <Stack direction="row" spacing={2}>
      <TextField
        label="Row"
        type="number"
        name={constructFieldName(props.namePrefix, "row")}
        value={row}
        onChange={(event) => {
          const newRow = parseInt(event.target.value, 10);
          if (isNaN(newRow)) {
            return;
          }
          setRow(newRow);
          props.onRowAndColChange?.(newRow, col);
        }}
        disabled={!props.inputsEnabled}
        fullWidth
        inputProps={{ min: 0, readOnly: true }}
      />
      <TextField
        label="Column"
        type="number"
        name={constructFieldName(props.namePrefix, "col")}
        value={col}
        onChange={(event) => {
          const newCol = parseInt(event.target.value, 10);
          if (isNaN(newCol)) {
            return;
          }
          setCol(newCol);
          props.onRowAndColChange?.(row, newCol);
        }}
        disabled={!props.inputsEnabled}
        fullWidth
        inputProps={{ 
          min: 0, 
          readOnly: true,
        }}
      />
    </Stack>
  );
} 