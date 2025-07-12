import { Box, useTheme } from "@mui/material";

interface BigPlanDonePctBigTagProps {
  donePct: number;
  shouldShowMilestonesLeft: boolean;    
  milestonesLeft: number;
}

export function BigPlanDonePctBigTag(props: BigPlanDonePctBigTagProps) {
  const theme = useTheme();

  const milestonePlural = props.milestonesLeft === 1 ? "milestone" : "milestones";

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
        backgroundColor: theme.palette.grey[500],
        color: theme.palette.primary.contrastText,
        height: "100%",
      }}
    >
      Done {props.donePct}%
      {props.shouldShowMilestonesLeft &&
        props.milestonesLeft > 0 &&
        ` (${props.milestonesLeft} ${milestonePlural} left)`}
    </Box>
  );
}
