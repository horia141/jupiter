import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  Outlet,
  ShouldRevalidateFunction,
  useFetcher,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { NoteSource, WorkspaceFeature, type Note } from "jupiter-gen";
import { useContext } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
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

const QuerySchema = {
  source: z.nativeEnum(NoteSource).optional(),
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);

  const source = query.source ?? NoteSource.USER;

  const body = await getLoggedInApiClient(session).note.findNote({
    source: source,
    allow_archived: false,
    include_subnotes: false,
  });

  return json({
    source: source,
    entries: body.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Notes() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();
  const isBigScreen = useBigScreen();

  const archiveNoteFetch = useFetcher();

  function archiveNote(note: Note) {
    archiveNoteFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/notes/${note.ref_id.the_id}`,
      }
    );
  }

  let extraControls = [];
  if (isBigScreen) {
    extraControls = [
      <ButtonGroup>
        <Button
          variant={
            loaderData.source === NoteSource.USER ? "contained" : "outlined"
          }
          component={Link}
          to={`/workspace/notes?source=${NoteSource.USER}`}
        >
          🗒️ User
        </Button>

        <Button
          variant={
            loaderData.source === NoteSource.INBOX_TASK
              ? "contained"
              : "outlined"
          }
          component={Link}
          to={`/workspace/notes?source=${NoteSource.INBOX_TASK}`}
        >
          📥 Inbox Tasks
        </Button>

        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.METRICS
        ) && (
          <Button
            variant={
              loaderData.source === NoteSource.METRIC_ENTRY
                ? "contained"
                : "outlined"
            }
            component={Link}
            to={`/workspace/notes?source=${NoteSource.METRIC_ENTRY}`}
          >
            📈 Metrics
          </Button>
        )}

        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.PERSONS
        ) && (
          <Button
            variant={
              loaderData.source === NoteSource.PERSON ? "contained" : "outlined"
            }
            component={Link}
            to={`/workspace/notes?source=${NoteSource.PERSON}`}
          >
            👨 Persons
          </Button>
        )}
      </ButtonGroup>,
    ];
  } else {
    extraControls = [
      <Button
        variant={
          loaderData.source === NoteSource.USER ? "contained" : "outlined"
        }
        component={Link}
        to={`/workspace/notes?source=${NoteSource.USER}`}
      >
        🗒️ User
      </Button>,
      <Button
        variant={
          loaderData.source === NoteSource.INBOX_TASK ? "contained" : "outlined"
        }
        component={Link}
        to={`/workspace/notes?source=${NoteSource.INBOX_TASK}`}
      >
        📥 Inbox Tasks
      </Button>,
    ];

    if (
      isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.METRICS
      )
    ) {
      extraControls.push(
        <Button
          variant={
            loaderData.source === NoteSource.METRIC_ENTRY
              ? "contained"
              : "outlined"
          }
          component={Link}
          to={`/workspace/notes?source=${NoteSource.METRIC_ENTRY}`}
        >
          📈 Metrics
        </Button>
      );
    }

    if (
      isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.PERSONS
      )
    ) {
      extraControls.push(
        <Button
          variant={
            loaderData.source === NoteSource.PERSON ? "contained" : "outlined"
          }
          component={Link}
          to={`/workspace/notes?source=${NoteSource.PERSON}`}
        >
          👨 Persons
        </Button>
      );
    }
  }

  return (
    <TrunkPanel
      createLocation="/workspace/notes/new"
      extraControls={extraControls}
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={entry.note.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveNote(entry.note)}
            >
              <EntityLink to={`/workspace/notes/${entry.note.ref_id.the_id}`}>
                <EntityNameComponent name={entry.note.name} />
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
  () => `There was an error loading the notes! Please try again!`
);
