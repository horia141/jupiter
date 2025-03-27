import type { ProjectSummary } from "@jupiter/webapi-client";
import { ApiError, NoteDomain } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useNavigation } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";

import { makeLeafCatchBoundary } from "~/components/infra/catch-boundary";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/project-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isRootProject } from "~/logic/domain/project";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation as useLoaderDataForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
  }),
  z.object({
    intent: z.literal("change-parent"),
    parentProjectRefId: z.string(),
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const response = await apiClient.projects.projectLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      rootProject: summaryResponse.root_project as ProjectSummary,
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
      project: response.project,
      note: response.note,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.NOT_FOUND) {
      throw new Response(ReasonPhrases.NOT_FOUND, {
        status: StatusCodes.NOT_FOUND,
        statusText: ReasonPhrases.NOT_FOUND,
      });
    }

    throw error;
  }
}

export async function action({ request, params }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.projects.projectUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
        });

        return redirect(`/app/workspace/projects`);
      }

      case "change-parent": {
        await apiClient.projects.projectChangeParent({
          ref_id: id,
          parent_project_ref_id: form.parentProjectRefId,
        });

        return redirect(`/app/workspace/projects`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.PROJECT,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/projects/${id}`);
      }

      case "archive": {
        await apiClient.projects.projectArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/projects`);
      }

      case "remove": {
        await apiClient.projects.projectRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/projects`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
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

export default function Project() {
  const loaderData = useLoaderDataForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.project.archived;

  const parentProject = loaderData.allProjects.find(
    (project) => project.ref_id === loaderData.project.parent_project_ref_id,
  );
  const [selectedProject, setSelectedProject] = useState(
    parentProject === undefined
      ? loaderData.rootProject.ref_id
      : parentProject.ref_id,
  );

  useEffect(() => {
    const parentProject = loaderData.allProjects.find(
      (project) => project.ref_id === loaderData.project.parent_project_ref_id,
    );
    setSelectedProject(
      parentProject === undefined
        ? loaderData.rootProject.ref_id
        : parentProject.ref_id,
    );
  }, [loaderData]);

  return (
    <LeafPanel
      key={`projects-${loaderData.project.ref_id}`}
      showArchiveAndRemoveButton={!isRootProject(loaderData.project)}
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.project.archived}
      returnLocation="/app/workspace/projects"
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <ProjectSelect
                name="parentProjectRefId"
                label="Parent Project"
                inputsEnabled={
                  inputsEnabled && !isRootProject(loaderData.project)
                }
                disabled={false}
                allProjects={loaderData.allProjects}
                value={selectedProject}
                onChange={setSelectedProject}
              />

              <FieldError
                actionResult={actionData}
                fieldName="/parent_project_ref_id"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.project.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>

            <Button
              variant="outlined"
              disabled={!inputsEnabled || isRootProject(loaderData.project)}
              type="submit"
              name="intent"
              value="change-parent"
            >
              Change Parent
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      <Card>
        {!loaderData.note && (
          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeLeafCatchBoundary(
  "/app/workspace/projects",
  () => `Could not find project #${useParams().id}!`,
);

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/projects",
  () =>
    `There was an error loading project #${useParams().id}! Please try again!`,
);
