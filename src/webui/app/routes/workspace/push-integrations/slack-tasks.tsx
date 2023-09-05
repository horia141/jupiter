import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  ShouldRevalidateFunction,
  useFetcher,
  useOutlet,
} from "@remix-run/react";
import { WorkspaceFeature, type SlackTask } from "jupiter-gen";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { ADateTag } from "~/components/adate-tag";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
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
  const response = await getLoggedInApiClient(session).slackTask.findSlackTask({
    allow_archived: false,
    include_inbox_tasks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function SlackTasks() {
  const outlet = useOutlet();
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
        action: `/workspace/push-integrations/slack-tasks/${slackTask.ref_id.the_id}`,
      }
    );
  }

  return (
    <TrunkCard>
      <NestingAwarePanel showOutlet={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <Button
              variant="contained"
              to="/workspace/push-integrations/slack-tasks/settings"
              component={Link}
              preventScrollReset
            >
              Setings
            </Button>
          )}
        </ActionHeader>

        <EntityStack>
          {sortedEntries.map((entry) => (
            <EntityCard
              key={entry.slack_task.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveSlackTask(entry.slack_task)}
            >
              <EntityLink
                to={`/workspace/push-integrations/slack-tasks/${entry.slack_task.ref_id.the_id}`}
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
      </NestingAwarePanel>

      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the Slack tasks!s Please try again!`
);
