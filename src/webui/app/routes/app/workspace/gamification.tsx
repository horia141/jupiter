import { Card, CardContent, CardHeader, Stack } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { ScoreHistory } from "~/components/gamification/score-history";
import { ScoreOverview } from "~/components/gamification/score-overview";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const result = await apiClient.users.userLoad({});

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
    <TrunkPanel key={"gamification"} returnLocation="/app/workspace">
      <ToolPanel>
        <Stack useFlexGap gap={2}>
          {loaderData.userScoreOverview && (
            <Card>
              <CardHeader title="💪 Scores Overview" />
              <CardContent>
                <ScoreOverview scoreOverview={loaderData.userScoreOverview} />
              </CardContent>
            </Card>
          )}
          {loaderData.userScoreHistory && (
            <Card>
              <CardHeader title="💪 Scores History" />
              <CardContent>
                <ScoreHistory scoreHistory={loaderData.userScoreHistory} />
              </CardContent>
            </Card>
          )}
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () =>
    `There was an error displaying gamification information! Please try again!`,
});
