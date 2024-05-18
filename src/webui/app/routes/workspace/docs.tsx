import type { Doc } from "@jupiter/webapi-client";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useFetcher } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
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

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));

  const body = await getLoggedInApiClient(session).docs.docFind({
    include_notes: false,
    allow_archived: false,
    include_subdocs: false,
  });

  return json({
    entries: body.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Docs() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const archiveDocFetch = useFetcher();

  function archiveDoc(doc: Doc) {
    archiveDocFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/docs/${doc.ref_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      key={"docs"}
      createLocation="/workspace/docs/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={`doc-${entry.doc.ref_id}`}
              entityId={`doc-${entry.doc.ref_id}`}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveDoc(entry.doc)}
            >
              <EntityLink to={`/workspace/docs/${entry.doc.ref_id}`}>
                <EntityNameComponent name={entry.doc.name} />
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
  () => `There was an error loading the docs! Please try again!`
);
