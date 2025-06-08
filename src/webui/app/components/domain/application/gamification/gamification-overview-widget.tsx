import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";
import { ScoreOverview } from "~/components/domain/application/gamification/score-overview";
import { StandardDivider } from "~/components/infra/standard-divider";

export function GamificationOverviewWidget(props: WidgetProps) {
  const gamification = props.gamificationOverview!;

  return (
    <WidgetContainer>
      <StandardDivider title="Your Scores" size="large" />
      <ScoreOverview scoreOverview={gamification} />
    </WidgetContainer>
  );
}
