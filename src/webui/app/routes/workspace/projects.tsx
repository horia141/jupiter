import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, useOutlet } from "@remix-run/react";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
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

export default function Projects() {
  const projects = useLoaderDataSafeForAnimation<typeof loader>();
  const outlet = useOutlet();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  return (
    <TrunkCard>
      <NestingAwarePanel showOutlet={shouldShowALeaf}>
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
      </NestingAwarePanel>

      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the projects! Please try again!`
);
