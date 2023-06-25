import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useFetcher, useOutlet } from "@remix-run/react";
import type { EmailTask } from "jupiter-gen";
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
import { TrunkCard } from "~/components/infra/trunk-card";
import { emailTaskNiceName } from "~/logic/domain/email-task";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).emailTask.findEmailTask({
    allow_archived: false,
    include_inbox_task: false,
  });
  return json(response.entries);
}

export default function EmailTasks() {
  const outlet = useOutlet();
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedEntries = [...entries];

  const archiveEmailTaskFetch = useFetcher();

  function archiveEmailTask(emailTask: EmailTask) {
    archiveEmailTaskFetch.submit(
      {
        intent: "archive",
        fromAddress: "NOT USED - FOR ARCHIVE ONLY",
        fromName: "NOT USED - FOR ARCHIVE ONLY",
        toAddress: "NOT USED - FOR ARCHIVE ONLY",
        subject: "NOT USED - FOR ARCHIVE ONLY",
        body: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/push-integrations/email-tasks/${emailTask.ref_id.the_id}`,
      }
    );
  }

  return (
    <TrunkCard>
      <ActionHeader returnLocation="/workspace">
        <Button
          variant="contained"
          to="/workspace/push-integrations/email-tasks/settings"
          component={Link}
        >
          Setings
        </Button>
      </ActionHeader>

      <EntityStack>
        {sortedEntries.map((entry) => (
          <EntityCard
            key={entry.email_task.ref_id.the_id}
            allowSwipe
            allowMarkNotDone
            onMarkNotDone={() => archiveEmailTask(entry.email_task)}
          >
            <EntityLink
              to={`/workspace/push-integrations/email-tasks/${entry.email_task.ref_id.the_id}`}
            >
              <EntityNameComponent
                name={emailTaskNiceName(entry.email_task as EmailTask)}
              />
              {entry.email_task.generation_extra_info.actionable_date && (
                <ADateTag
                  label="Actionabel From"
                  date={entry.email_task.generation_extra_info.actionable_date}
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
                  difficulty={entry.email_task.generation_extra_info.difficulty}
                />
              )}
            </EntityLink>
          </EntityCard>
        ))}
      </EntityStack>

      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the email tasks! Please try again!`
);
