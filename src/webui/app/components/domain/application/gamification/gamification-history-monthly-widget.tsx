import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";
import { ScoreHistory } from "~/components/domain/application/gamification/score-history";

export function GamificationHistoryMonthlyWidget(props: WidgetProps) {
  const gamification = props.gamificationHistory!;

  return (
    <WidgetContainer>
      <ScoreHistory
        scoreHistory={{
          daily_scores: [],
          weekly_scores: [],
          monthly_scores: gamification.monthly_scores,
          quarterly_scores: [],
        }}
      />
    </WidgetContainer>
  );
}
