import type { ScheduleStreamSummary } from "@jupiter/webapi-client";
import { Box, Chip, MenuItem, Select } from "@mui/material";

import { ScheduleStreamColorTag } from "~/components/domain/concept/schedule/schedule-stream-color-tag";

interface ScheduleStreamMultiSelectProps {
  labelId: string;
  label: string;
  name: string;
  readOnly: boolean;
  allScheduleStreams: Array<ScheduleStreamSummary>;
}

export function ScheduleStreamMultiSelect(
  props: ScheduleStreamMultiSelectProps,
) {
  const allScheduleStreamsByRefId = new Map(
    props.allScheduleStreams.map((st) => [st.ref_id, st]),
  );
  return (
    <Select
      labelId={props.labelId}
      label={props.label}
      name={props.name}
      readOnly={props.readOnly}
      disabled={props.readOnly}
      multiple
      defaultValue={[]}
      renderValue={(selected) => (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
          {selected.map((value) => (
            <Chip
              key={value}
              label={allScheduleStreamsByRefId.get(value)!.name}
            />
          ))}
        </Box>
      )}
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
