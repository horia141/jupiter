import type { ScheduleStreamColor } from "@jupiter/webapi-client";
import { Box } from "@mui/material";

import { scheduleStreamColorHex } from "~/logic/domain/schedule-stream-color";

interface ScheduleStreamColorTagProps {
  color: ScheduleStreamColor;
}

export function ScheduleStreamColorTag(props: ScheduleStreamColorTagProps) {
  return (
    <Box
      sx={{
        display: "inline-block",
        borderRadius: "0.5rem",
        width: "1em",
        height: "1em",
        backgroundColor: scheduleStreamColorHex(props.color),
      }}
    ></Box>
  );
}
