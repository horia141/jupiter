import { Box, Chip, MenuItem, Select } from "@mui/material";
import { RecurringTaskPeriod } from "jupiter-gen";
import { periodName } from "~/logic/domain/period";

interface PeriodSelectProps {
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
}

export function PeriodSelect(props: PeriodSelectProps) {
  return (
    <Select
      labelId={props.labelId}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      multiple
      defaultValue={[]}
      renderValue={(selected) => (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
          {selected.map((value) => (
            <Chip key={value} label={periodName(value)} />
          ))}
        </Box>
      )}
      label={props.label}
    >
      {Object.values(RecurringTaskPeriod).map((st) => (
        <MenuItem key={st} value={st}>
          {periodName(st)}
        </MenuItem>
      ))}
    </Select>
  );
}
