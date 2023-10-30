import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, Outlet, ShouldRevalidateFunction } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
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
  const response = await getLoggedInApiClient(session).project.findProject({
    allow_archived: false,
  });
  return json(response.projects);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Projects() {
  const projects = useLoaderDataSafeForAnimation<typeof loader>();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  return (
    <TrunkPanel>
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          <Button
            variant="contained"
            to="/workspace/projects/new"
            component={Link}
          >
            Create
          </Button>
        </ActionHeader>

        <EntityStack>
          {projects.map((project) => (
            <EntityCard key={project.ref_id.the_id}>
              <EntityLink to={`/workspace/projects/${project.ref_id.the_id}`}>
                <EntityNameComponent name={project.name} />
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
  () => `There was an error loading the projects! Please try again!`
);
