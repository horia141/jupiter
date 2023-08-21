import { Card, CardContent, CardHeader } from "@mui/material";
import { ShouldRevalidateFunction } from "@remix-run/react";
import { useContext } from "react";
import { ScoreOverview } from "~/components/gamification/score-overview";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { ToolCard } from "~/components/infra/tool-card";
import { ToolPanel } from "~/components/infra/tool-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function Gamification() {
  const isBigScreen = useBigScreen();
  const topLevelInfo = useContext(TopLevelInfoContext);

  return (
    <TrunkCard>
      <ToolPanel show={true}>
        <ToolCard returnLocation="/workspace">
          {topLevelInfo.userScoreOverview && (
            <Card>
              <CardHeader title="💪 Scores" />
              <CardContent>
                <ScoreOverview scoreOverview={topLevelInfo.userScoreOverview} />
              </CardContent>
            </Card>
          )}
        </ToolCard>
      </ToolPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error displaying gamification information! Please try again!`
);
