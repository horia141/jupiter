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
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <ScheduleStreamColorTag color={st} />
            <Box sx={{ paddingLeft: "1rem" }}>
              {scheduleStreamColorName(st)}
            </Box>
          </Box>
        </MenuItem>
      ))}
    </Select>
  );
}
