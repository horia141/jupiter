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
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/infra/entity-note-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/domain/concept/project/project-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isRootProject } from "~/logic/domain/project";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation as useLoaderDataForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { SectionCard } from "~/components/infra/section-card";
import { SectionActions } from "~/components/infra/section-actions";
import { ActionSingle } from "~/components/infra/section-actions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
});

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

export async function loader({ request, params }: LoaderFunctionArgs) {
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

export async function action({ request, params }: ActionFunctionArgs) {
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
  const topLevelInfo = useContext(TopLevelInfoContext);
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
      fakeKey={`projects-${loaderData.project.ref_id}`}
      showArchiveAndRemoveButton={!isRootProject(loaderData.project)}
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.project.archived}
      returnLocation="/app/workspace/projects"
    >
      <GlobalError actionResult={actionData} />
      <SectionCard title="Properties"
        actions={
          <SectionActions
            id="project-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Save",
                value: "update",
                highlight: true,
              }),
              ActionSingle({
                text: "Change Parent",
                value: "change-parent",
                highlight: false,
              }),
            ]} />
        }
      >
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
      </SectionCard>

      <SectionCard title="Note"
        actions={
          <SectionActions
            id="project-note"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Create Note",
                value: "create-note",
                highlight: false,
                disabled: loaderData.note !== null,
              }),
            ]} />
          }
      >
        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/projects",
  ParamsSchema,
  {
    notFound: (params) => `Could not find project with ID ${params.id}!`,
    error: (params) =>
      `There was an error loading project with ID ${params.id}! Please try again!`,
  },
);
