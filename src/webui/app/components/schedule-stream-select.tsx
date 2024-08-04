import type { ScheduleStreamSummary } from "@jupiter/webapi-client";
import { MenuItem, Select } from "@mui/material";

interface ScheduleStreamSelectProps {
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
  allScheduleStreams: Array<ScheduleStreamSummary>;
  value: ScheduleStreamSummary;
}

export function ScheduleStreamSelect(props: ScheduleStreamSelectProps) {
  return (
    <Select
      labelId={props.labelId}
      label={props.label}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      defaultValue={props.value.ref_id}
    >
      {props.allScheduleStreams.map((st) => (
        <MenuItem key={st.ref_id} value={st.ref_id}>
          {st.name}
        </MenuItem>
      ))}
    </Select>
  );
}
