import type { ScheduleStreamSummary } from "@jupiter/webapi-client";
import { Box, MenuItem, Select } from "@mui/material";
import { ScheduleStreamColorTag } from "./schedule-stream-color-tag";

interface ScheduleStreamSelectProps {
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
  allScheduleStreams: Array<ScheduleStreamSummary>;
  defaultValue: ScheduleStreamSummary;
}

export function ScheduleStreamSelect(props: ScheduleStreamSelectProps) {
  return (
    <Select
      labelId={props.labelId}
      label={props.label}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      defaultValue={props.defaultValue.ref_id}
    >
      {props.allScheduleStreams.map((st) => (
        <MenuItem key={st.ref_id} value={st.ref_id}>
          <Box sx={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            {st.name}
            <ScheduleStreamColorTag color={st.color} />
          </Box>
        </MenuItem>
      ))}
    </Select>
  );
}
