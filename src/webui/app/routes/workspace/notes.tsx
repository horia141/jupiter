import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Outlet, ShouldRevalidateFunction, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import type { Note } from "jupiter-gen";
import { useContext } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
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
  const body = await getLoggedInApiClient(session).note.findNote({
    allow_archived: false,
    include_subnotes: false,
  });

  return json({
    entries: body.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Notes() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

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

  return (
    <TrunkPanel
      createLocation="/workspace/notes/new"
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
