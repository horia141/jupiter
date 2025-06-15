import type { ProjectSummary } from "@jupiter/webapi-client";
import { ApiError } from "@jupiter/webapi-client";
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
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/domain/concept/project/project-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = z.object({});

const CreateFormSchema = z.object({
  parentProjectRefId: z.string(),
  name: z.string(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  return json({
    rootProject: summaryResponse.root_project as ProjectSummary,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const response = await apiClient.projects.projectCreate({
      parent_project_ref_id: form.parentProjectRefId,
      name: form.name,
    });

    return redirect(`/app/workspace/projects/${response.new_project.ref_id}`);
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

export default function NewProject() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      fakeKey={"projects/new"}
      returnLocation="/app/workspace/projects"
      inputsEnabled={inputsEnabled}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <ProjectSelect
                name="parentProjectRefId"
                label="Parent Project"
                inputsEnabled={inputsEnabled}
                disabled={false}
                allProjects={loaderData.allProjects}
                defaultValue={loaderData.rootProject.ref_id}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/parent_project_ref_id"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                type="text"
                placeholder="Project name"
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="project-create"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="create"
            >
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/projects",
  ParamsSchema,
  {
    notFound: () => `Could not find the project!`,
    error: () => `There was an error creating the project! Please try again!`,
  },
);
