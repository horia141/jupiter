import type { BigPlanStatus } from "@jupiter/webapi-client";
import { Box, useTheme } from "@mui/material";
import {
  bigPlanStatusIcon,
  bigPlanStatusName,
} from "~/logic/domain/big-plan-status";
import { useBigScreen } from "~/rendering/use-big-screen";

interface BigPlanStatusBigTagProps {
  status: BigPlanStatus;
}

export function BigPlanStatusBigTag(props: BigPlanStatusBigTagProps) {
  const isBigScreen = useBigScreen();
  const tagName = bigPlanStatusName(props.status);
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
      {isBigScreen ? tagName : bigPlanStatusIcon(props.status)}
    </Box>
  );
}
