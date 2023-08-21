import { Box, Divider, Typography } from "@mui/material";
import { UserScoreOverview } from "jupiter-gen";
import { useBigScreen } from "~/rendering/use-big-screen";

interface ScoreOverviewProps {
  scoreOverview: UserScoreOverview;
}

export function ScoreOverview(props: ScoreOverviewProps) {
  const isBigScreen = useBigScreen();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: isBigScreen ? "row" : "column",
        gap: "0.5rem",
        justifyContent: "space-evenly",
      }}
    >
      <Typography variant="h6">
        Daily: {props.scoreOverview.daily_score}
      </Typography>
      <Divider orientation={isBigScreen ? "vertical" : "horizontal"} flexItem />
      <Typography variant="h6">
        Weekly: {props.scoreOverview.weekly_score}
      </Typography>
      <Divider orientation={isBigScreen ? "vertical" : "horizontal"} flexItem />
      <Typography variant="h6">
        Monthly: {props.scoreOverview.monthly_score}
      </Typography>
      <Divider orientation={isBigScreen ? "vertical" : "horizontal"} flexItem />
      <Typography variant="h6">
        Quarterly: {props.scoreOverview.quarterly_score}
      </Typography>
      <Divider orientation={isBigScreen ? "vertical" : "horizontal"} flexItem />
      <Typography variant="h6">
        Yearly: {props.scoreOverview.yearly_score}
      </Typography>
      <Divider orientation={isBigScreen ? "vertical" : "horizontal"} flexItem />
      <Typography variant="h6">
        Lifetime: {props.scoreOverview.lifetime_score}
      </Typography>
    </Box>
  );
}
