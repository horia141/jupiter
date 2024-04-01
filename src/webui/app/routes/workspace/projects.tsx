import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import { IconButton } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Form, Outlet, useActionData } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import {
  computeProjectDistanceFromRoot,
  isRootProject,
  shiftProjectDownInListOfChildren,
  shiftProjectUpInListOfChildren,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { getIntent, makeIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const UpdateFormSchema = {
  intent: z.string(),
};

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).projects.projectFind({
    allow_archived: false,
    include_notes: false,
  });
  return json(response.entries);
}

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  const { intent, args } = getIntent<{
    refId: string;
    newOrderOfChildProjects: string[];
  }>(form.intent);

  try {
    switch (intent) {
      case "reorder": {
        if (!args?.refId || !args?.newOrderOfChildProjects) {
          throw new Error("Missing required arguments!");
        }

        await getLoggedInApiClient(session).projects.projectReorderChildren({
          ref_id: args?.refId,
          new_order_of_child_projects: args?.newOrderOfChildProjects,
        });

        return redirect("/workspace/projects");
      }

      default: {
        throw new Error(`Unhandled intent: ${intent}`);
      }
    }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Projects() {
  const projects = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedProjects = sortProjectsByTreeOrder(
    projects.map((entry) => entry.project)
  );
  const allProjectsByRefId = new Map(
    projects.map((entry) => [entry.project.ref_id, entry.project])
  );

  return (
    <TrunkPanel
      createLocation="/workspace/projects/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <GlobalError actionResult={actionData} />
        <EntityStack>
          <Form method="post">
            {sortedProjects.map((project) => {
              const parentProject = project.parent_project_ref_id
                ? allProjectsByRefId.get(project.parent_project_ref_id)
                : undefined;
              const indent = computeProjectDistanceFromRoot(
                project,
                allProjectsByRefId
              );
              return (
                <EntityCard
                  key={project.ref_id}
                  indent={indent}
                  extraControls={
                    isRootProject(project) ||
                    parentProject === undefined ? undefined : (
                      <>
                        <IconButton
                          size="medium"
                          type="submit"
                          name="intent"
                          value={makeIntent("reorder", {
                            refId: parentProject.ref_id,
                            newOrderOfChildProjects:
                              shiftProjectUpInListOfChildren(
                                project,
                                parentProject.order_of_child_projects
                              ),
                          })}
                        >
                          <ArrowUpwardIcon fontSize="medium" />
                        </IconButton>

                        <IconButton
                          size="medium"
                          type="submit"
                          name="intent"
                          value={makeIntent("reorder", {
                            refId: parentProject.ref_id,
                            newOrderOfChildProjects:
                              shiftProjectDownInListOfChildren(
                                project,
                                parentProject.order_of_child_projects
                              ),
                          })}
                        >
                          <ArrowDownwardIcon fontSize="medium" />
                        </IconButton>
                      </>
                    )
                  }
                >
                  <EntityLink to={`/workspace/projects/${project.ref_id}`}>
                    <EntityNameComponent name={project.name} />
                  </EntityLink>
                </EntityCard>
              );
            })}
          </Form>
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
