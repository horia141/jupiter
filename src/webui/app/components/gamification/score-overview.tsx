import {
  Box,
  styled,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import type { UserScore, UserScoreOverview } from "jupiter-gen";
import { useBigScreen } from "~/rendering/use-big-screen";

interface ScoreOverviewProps {
  scoreOverview: UserScoreOverview;
}

export function ScoreOverview(props: ScoreOverviewProps) {
  const isBigScreen = useBigScreen();

  return (
    <TableContainer component={Box}>
      <Table
        sx={{ tableLayout: "fixed" }}
        size={isBigScreen ? "small" : "medium"}
      >
        <TableHead>
          <TableRow>
            <SmallTableCell width="20%">Period</SmallTableCell>
            <SmallTableCell width="20%">Current</SmallTableCell>
            <SmallTableCell width="20%">Best This Quarter</SmallTableCell>
            <SmallTableCell width="20%">Best This Year</SmallTableCell>
            <SmallTableCell width="20%">Best Ever</SmallTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Daily</TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.daily_score} />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_quarterly_daily_score}
              />
            </TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.best_yearly_daily_score} />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_lifetime_daily_score}
              />
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell>Weekly</TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.weekly_score} />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_quarterly_weekly_score}
              />
            </TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.best_yearly_weekly_score} />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_lifetime_weekly_score}
              />
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell>Monthly</TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.monthly_score} />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_quarterly_monthly_score}
              />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_yearly_monthly_score}
              />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_lifetime_monthly_score}
              />
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell>Quarterly</TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.quarterly_score} />
            </TableCell>
            <TableCell>N/A</TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_yearly_quarterly_score}
              />
            </TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_lifetime_quarterly_score}
              />
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell>Yearly</TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.yearly_score} />
            </TableCell>
            <TableCell>N/A</TableCell>
            <TableCell>N/A</TableCell>
            <TableCell>
              <Score
                userScore={props.scoreOverview.best_lifetime_yearly_score}
              />
            </TableCell>
          </TableRow>

          <TableRow>
            <TableCell>Lifetime</TableCell>
            <TableCell>
              <Score userScore={props.scoreOverview.lifetime_score} />
            </TableCell>
            <TableCell>N/A</TableCell>
            <TableCell>N/A</TableCell>
            <TableCell>N/A</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
}

const SmallTableCell = styled(TableCell)`
  font-size: 0.75rem;
  font-weight: bold;
`;

interface ScoreProps {
  userScore: UserScore;
}

function Score({ userScore }: ScoreProps) {
  const isBigScreen = useBigScreen();

  if (!isBigScreen) {
    return <>{userScore.total_score}</>;
  }

  if (userScore.inbox_task_cnt > 0 && userScore.big_plan_cnt > 0) {
    return (
      <>
        {userScore.total_score} 📥 {userScore.inbox_task_cnt} 🌍{" "}
        {userScore.big_plan_cnt}
      </>
    );
  } else if (userScore.inbox_task_cnt > 0 && userScore.big_plan_cnt === 0) {
    return (
      <>
        {userScore.total_score} 📥 {userScore.inbox_task_cnt}
      </>
    );
  } else if (userScore.inbox_task_cnt === 0 && userScore.big_plan_cnt > 0) {
    return (
      <>
        {userScore.total_score} 🌍 {userScore.big_plan_cnt}
      </>
    );
  } else {
    return <>{userScore.total_score}</>;
  }
}
