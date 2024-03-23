import {
  Autocomplete,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
  TextField,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { ProjectSummary } from "jupiter-gen";
import { ApiError, NoteDomain } from "jupiter-gen";
import { useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation as useLoaderDataForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  parentProjectRefId: z.string().optional(),
  name: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const response = await getLoggedInApiClient(session).projects.projectLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
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
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "update": {
        await getLoggedInApiClient(session).projects.projectUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
        });

        return redirect(`/workspace/projects/${id}`);
      }

      case "change-parent": {
        await getLoggedInApiClient(session).projects.projectChangeParent({
          ref_id: id,
          parent_project_ref_id:
            form.parentProjectRefId !== undefined &&
            form.parentProjectRefId !== "none"
              ? form.parentProjectRefId
              : undefined,
        });

        return redirect(`/workspace/projects/${id}`);
      }

      case "create-note": {
        await getLoggedInApiClient(session).core.noteCreate({
          domain: NoteDomain.PROJECT,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/workspace/projects/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).projects.projectArchive({
          ref_id: id,
        });

        return redirect(`/workspace/projects/${id}`);
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
  const transition = useTransition();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.project.archived;

  const parentProject = loaderData.allProjects.find(
    (project) => project.ref_id === loaderData.project.parent_project_ref_id
  );
  const [selectedProject, setSelectedProject] = useState(
    parentProject === undefined
      ? { project_ref_id: "none", label: "none" }
      : { project_ref_id: parentProject.ref_id, label: parentProject.name }
  );

  const allProjectsAsOptions = [
    {
      project_ref_id: "none",
      label: "None",
    },
  ].concat(
    loaderData.allProjects.map((project) => ({
      project_ref_id: project.ref_id,
      label: project.name,
    }))
  );

  useEffect(() => {
    const parentProject = loaderData.allProjects.find(
      (project) => project.ref_id === loaderData.project.parent_project_ref_id
    );
    setSelectedProject(
      parentProject === undefined
        ? { project_ref_id: "none", label: "none" }
        : { project_ref_id: parentProject.ref_id, label: parentProject.name }
    );
  }, [loaderData]);

  return (
    <LeafPanel
      key={loaderData.project.ref_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/projects"
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <Autocomplete
                id="parentProject"
                options={allProjectsAsOptions}
                readOnly={!inputsEnabled}
                value={selectedProject}
                disableClearable={true}
                onChange={(e, v) => setSelectedProject(v)}
                isOptionEqualToValue={(o, v) =>
                  o.project_ref_id === v.project_ref_id
                }
                renderInput={(params) => (
                  <TextField {...params} label="Parent Project" />
                )}
              />

              <FieldError
                actionResult={actionData}
                fieldName="/parent_project_ref_id"
              />

              <input
                type="hidden"
                name="parentProjectRefId"
                value={selectedProject.project_ref_id}
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
              disabled={!inputsEnabled}
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

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find project #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading project #${useParams().id}! Please try again!`
);
