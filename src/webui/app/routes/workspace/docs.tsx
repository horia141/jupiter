import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { getLoggedInApiClient } from "~/api-clients.server";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const body = await apiClient.docs.docFind({
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

  return (
    <TrunkPanel
      key={"docs"}
      createLocation="/workspace/docs/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {loaderData.entries.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no docs to show. You can create a new doc."
            newEntityLocations="/workspace/docs/new"
            helpSubject={DocsHelpSubject.DOCS}
          />
        )}

        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              key={`doc-${entry.doc.ref_id}`}
              entityId={`doc-${entry.doc.ref_id}`}
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

export const ErrorBoundary = makeTrunkErrorBoundary(
  "/workspace",
  () => `There was an error loading the docs! Please try again!`
);
