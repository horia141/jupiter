import { ScheduleStreamColor } from "@jupiter/webapi-client";
import { Box, MenuItem, Select } from "@mui/material";
import { scheduleStreamColorName } from "~/logic/domain/schedule-stream-color";
import { ScheduleStreamColorTag } from "./schedule-stream-color-tag";

interface ScheduleStreamColorInputProps {
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
  value: ScheduleStreamColor;
}

export function ScheduleStreamColorInput(props: ScheduleStreamColorInputProps) {
  return (
    <Select
      labelId={props.labelId}
      label={props.label}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      defaultValue={props.value}
    >
      {Object.values(ScheduleStreamColor).map((st) => (
        <MenuItem key={st} value={st}>
          <Box sx={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <ScheduleStreamColorTag color={st} />
            {scheduleStreamColorName(st)}
          </Box>
        </MenuItem>
      ))}
    </Select>
  );
}
