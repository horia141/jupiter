import { type EmailTask, WorkspaceFeature } from "@jupiter/webapi-client";
import { Button } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { ADateTag } from "~/components/adate-tag";
import { DifficultyTag } from "~/components/difficulty-tag";
import { EisenTag } from "~/components/eisen-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { emailTaskNiceName } from "~/logic/domain/email-task";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.email.emailTaskFind({
    allow_archived: false,
    include_inbox_task: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function EmailTasks() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedEntries = [...entries];

  return (
    <TrunkPanel
      key={"email-tasks"}
      extraControls={[
        <>
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS,
          ) && (
            <Button
              variant="contained"
              to="/app/workspace/push-integrations/email-tasks/settings"
              component={Link}
            >
              Setings
            </Button>
          )}
        </>,
      ]}
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {sortedEntries.map((entry) => (
            <EntityCard
              key={`email-task-${entry.email_task.ref_id}`}
              entityId={`email-task-${entry.email_task.ref_id}`}
            >
              <EntityLink
                to={`/app/workspace/push-integrations/email-tasks/${entry.email_task.ref_id}`}
              >
                <EntityNameComponent
                  name={emailTaskNiceName(entry.email_task as EmailTask)}
                />
                {entry.email_task.generation_extra_info.actionable_date && (
                  <ADateTag
                    label="Actionabel From"
                    date={
                      entry.email_task.generation_extra_info.actionable_date
                    }
                  />
                )}
                {entry.email_task.generation_extra_info.due_date && (
                  <ADateTag
                    label="Due At"
                    date={entry.email_task.generation_extra_info.due_date}
                  />
                )}
                {entry.email_task.generation_extra_info.eisen && (
                  <EisenTag
                    eisen={entry.email_task.generation_extra_info.eisen}
                  />
                )}
                {entry.email_task.generation_extra_info.difficulty && (
                  <DifficultyTag
                    difficulty={
                      entry.email_task.generation_extra_info.difficulty
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

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the email tasks! Please try again!`,
});
