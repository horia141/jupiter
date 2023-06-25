import { Box, Chip, MenuItem, Select } from "@mui/material";
import { SyncTarget } from "jupiter-gen";
import { syncTargetName } from "~/logic/domain/sync-target";

interface SyncTargetSelectProps {
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
}

export function SyncTargetSelect(props: SyncTargetSelectProps) {
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
            <Chip key={value} label={syncTargetName(value)} />
          ))}
        </Box>
      )}
      label={props.label}
    >
      {Object.values(SyncTarget).map((st) => (
        <MenuItem key={st} value={st}>
          {syncTargetName(st)}
        </MenuItem>
      ))}
    </Select>
  );
}
