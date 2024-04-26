import { WorkspaceFeature, type SlackTask } from "@jupiter/webapi-client";
import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { ADateTag } from "~/components/adate-tag";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { slackTaskNiceName } from "~/logic/domain/slack-task";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(
    session
  ).pushIntegrations.slackTaskFind({
    allow_archived: false,
    include_inbox_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function SlackTasks() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedEntries = [...entries];

  const archiveSlackTaskFetch = useFetcher();

  function archiveSlackTask(slackTask: SlackTask) {
    archiveSlackTaskFetch.submit(
      {
        intent: "archive",
        user: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/push-integrations/slack-tasks/${slackTask.ref_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      extraControls={[
        <>
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <Button
              variant="contained"
              to="/workspace/push-integrations/slack-tasks/settings"
              component={Link}
            >
              Setings
            </Button>
          )}
        </>,
      ]}
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedEntries.map((entry) => (
            <EntityCard
              key={`slack-task-${entry.slack_task.ref_id}`}
              entityId={`slack-task-${entry.slack_task.ref_id}`}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveSlackTask(entry.slack_task)}
            >
              <EntityLink
                to={`/workspace/push-integrations/slack-tasks/${entry.slack_task.ref_id}`}
              >
                <EntityNameComponent
                  name={slackTaskNiceName(entry.slack_task as SlackTask)}
                />
                {entry.slack_task.generation_extra_info.actionable_date && (
                  <ADateTag
                    label="Actionabel From"
                    date={
                      entry.slack_task.generation_extra_info.actionable_date
                    }
                  />
                )}
                {entry.slack_task.generation_extra_info.due_date && (
                  <ADateTag
                    label="Due At"
                    date={entry.slack_task.generation_extra_info.due_date}
                  />
                )}
                {entry.slack_task.generation_extra_info.eisen && (
                  <EisenTag
                    eisen={entry.slack_task.generation_extra_info.eisen}
                  />
                )}
                {entry.slack_task.generation_extra_info.difficulty && (
                  <DifficultyTag
                    difficulty={
                      entry.slack_task.generation_extra_info.difficulty
                    }
                  />
                )}
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the Slack tasks!s Please try again!`
);
