import { Card, CardContent, CardHeader } from "@mui/material";
import { json, LoaderArgs } from "@remix-run/node";
import { ShouldRevalidateFunction } from "@remix-run/react";
import { getLoggedInApiClient } from "~/api-clients";
import { ScoreHistory } from "~/components/gamification/score-history";
import { ScoreOverview } from "~/components/gamification/score-overview";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { ToolCard } from "~/components/infra/tool-card";
import { ToolPanel } from "~/components/infra/tool-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const result = await getLoggedInApiClient(session).user.loadUser({});

  return json({
    userScoreOverview: result.user_score_overview,
    userScoreHistory: result.user_score_history,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Gamification() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  return (
    <TrunkCard>
      <ToolPanel show={true}>
        <ToolCard returnLocation="/workspace">
          {loaderData.userScoreOverview && (
            <>
              <Card>
                <CardHeader title="💪 Scores Overview" />
                <CardContent>
                  <ScoreOverview scoreOverview={loaderData.userScoreOverview} />
                </CardContent>
              </Card>
              <Card>
                <CardHeader title="💪 Scores History" />
                <CardContent>
                  <ScoreHistory scoreHistory={loaderData.userScoreHistory} />
                </CardContent>
              </Card>
            </>
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
