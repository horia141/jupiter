import { styled, Typography } from "@mui/material";
import { ResponsiveLine } from "@nivo/line";
import type { UserScoreAtDate, UserScoreHistory } from "jupiter-gen";
import { aDateToDate } from "~/logic/domain/adate";
interface ScoreHistoryProps {
  scoreHistory: UserScoreHistory;
}

export function ScoreHistory(props: ScoreHistoryProps) {
  return (
    <>
      <ScoresGraph
        title="Daily Scores"
        scores={props.scoreHistory.daily_scores}
      />
      <ScoresGraph
        title="Weekly Scores"
        scores={props.scoreHistory.weekly_scores}
      />
      <ScoresGraph
        title="Monthly Scores"
        scores={props.scoreHistory.monthly_scores}
      />
      <ScoresGraph
        title="Quarterly Scores"
        scores={props.scoreHistory.quarterly_scores}
      />
    </>
  );
}

interface ScoresGraphProps {
  title: string;
  scores: Array<UserScoreAtDate>;
}

function ScoresGraph({ title, scores }: ScoresGraphProps) {
  if (scores.length <= 2) {
    return null;
  }

  const totalScoresForGraph = scores.map((score) => {
    return {
      x: aDateToDate(score.date).toFormat("yyyy-MM-dd"),
      y: score.total_score,
    };
  });
  const totalScoreMaxValue =
    Math.max(...totalScoresForGraph.map((entry) => entry.y)) * 1.35;

  const inboxTaskCntForGraph = scores.map((score) => {
    return {
      x: aDateToDate(score.date).toFormat("yyyy-MM-dd"),
      y: score.inbox_task_cnt,
    };
  });
  const bigPlanCntForGraph = scores.map((score) => {
    return {
      x: aDateToDate(score.date).toFormat("yyyy-MM-dd"),
      y: score.big_plan_cnt,
    };
  });

  return (
    <MetricGraphDiv>
      <Typography variant="h6">{title}</Typography>
      <ResponsiveLine
        curve="monotoneX"
        xScale={{
          type: "time",
          format: "%Y-%m-%d",
          useUTC: false,
          precision: "day",
        }}
        xFormat="time:%Y-%m-%d"
        yScale={{
          type: "linear",
          nice: true,
          min: 0,
          max: totalScoreMaxValue,
        }}
        axisBottom={{
          format: "%y-%b",
          tickValues: 7,
        }}
        pointSize={4}
        pointBorderWidth={1}
        pointBorderColor={{
          from: "color",
          modifiers: [["darker", 0.3]],
        }}
        margin={{ top: 20, right: 50, bottom: 110, left: 50 }}
        useMesh={true}
        enableSlices={false}
        legends={[
          {
            anchor: "bottom",
            direction: "row",
            justify: false,
            translateX: 0,
            translateY: 50,
            itemsSpacing: 0,
            itemDirection: "left-to-right",
            itemWidth: 100,
            itemHeight: 30,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: "circle",
            symbolBorderColor: "rgba(0, 0, 0, .5)",
          },
        ]}
        data={[
          {
            id: "Total Score",
            data: totalScoresForGraph,
          },
          {
            id: "Inbox Tasks",
            data: inboxTaskCntForGraph,
          },
          {
            id: "Big Plans",
            data: bigPlanCntForGraph,
          },
        ]}
      />
    </MetricGraphDiv>
  );
}

const MetricGraphDiv = styled("div")`
  height: 300px;
  margin-bottom: 2rem;
`;
