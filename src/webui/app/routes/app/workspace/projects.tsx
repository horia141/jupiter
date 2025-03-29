import { ApiError } from "@jupiter/webapi-client";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import { IconButton } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Form, Outlet, useActionData } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
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

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("reorder"),
  }),
]);

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.projects.projectFind({
    allow_archived: false,
    include_notes: false,
  });
  return json(response.entries);
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
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

        await apiClient.projects.projectReorderChildren({
          ref_id: args?.refId,
          new_order_of_child_projects: args?.newOrderOfChildProjects,
        });

        return redirect("/app/workspace/projects");
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
    projects.map((entry) => entry.project),
  );
  const allProjectsByRefId = new Map(
    projects.map((entry) => [entry.project.ref_id, entry.project]),
  );

  return (
    <TrunkPanel
      key={"projects"}
      createLocation="/app/workspace/projects/new"
      returnLocation="/app/workspace"
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
                allProjectsByRefId,
              );
              return (
                <EntityCard
                  entityId={`project-${project.ref_id}`}
                  key={`project-${project.ref_id}`}
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
                                parentProject.order_of_child_projects,
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
                                parentProject.order_of_child_projects,
                              ),
                          })}
                        >
                          <ArrowDownwardIcon fontSize="medium" />
                        </IconButton>
                      </>
                    )
                  }
                >
                  <EntityLink to={`/app/workspace/projects/${project.ref_id}`}>
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

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the projects! Please try again!`,
});
