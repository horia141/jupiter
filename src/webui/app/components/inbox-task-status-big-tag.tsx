import type { InboxTaskStatus } from "@jupiter/webapi-client";
import { Box, useTheme } from "@mui/material";
import {
  inboxTaskStatusIcon,
  inboxTaskStatusName,
} from "~/logic/domain/inbox-task-status";
import { useBigScreen } from "~/rendering/use-big-screen";

interface InboxTaskStatusBigTagProps {
  status: InboxTaskStatus;
}

export function InboxTaskStatusBigTag(props: InboxTaskStatusBigTagProps) {
  const isBigScreen = useBigScreen();
  const tagName = inboxTaskStatusName(props.status);
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: "flex",
        flexWrap: "wrap",
        alignContent: "center",
        justifyContent: "center",
        whiteSpace: "nowrap",
        borderRadius: "5px",
        padding: "0.5rem",
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText,
        height: "100%",
      }}
    >
      {isBigScreen ? tagName : inboxTaskStatusIcon(props.status)}
    </Box>
  );
}
