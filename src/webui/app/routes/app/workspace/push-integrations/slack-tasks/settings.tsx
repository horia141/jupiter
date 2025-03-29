import type { ProjectSummary } from "@jupiter/webapi-client";
import { ApiError, WorkspaceFeature } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  FormControl,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";

import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/project-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const UpdateFormSchema = {
  project: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  const slackTaskSettingsResponse = await apiClient.slack.slackTaskLoadSettings(
    {},
  );

  return json({
    generationProject: slackTaskSettingsResponse.generation_project,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    if (form.project === undefined) {
      throw new Error("Invalid application state");
    }

    await apiClient.slack.slackTaskChangeGenerationProject({
      generation_project_ref_id: form.project,
    });

    return redirect(`/app/workspace/push-integrations/slack-tasks/settings`);
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

export default function SlackTasksSettings() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={"slack-tasks/settings"}
      returnLocation="/app/workspace/push-integrations/slack-tasks"
      inputsEnabled={inputsEnabled}
    >
      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.PROJECTS,
      ) && (
        <Card>
          <GlobalError actionResult={actionData} />

          <CardHeader title="Generation Project" />
          <CardContent>
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <ProjectSelect
                  name="project"
                  label="Project"
                  inputsEnabled={inputsEnabled}
                  disabled={false}
                  allProjects={loaderData.allProjects}
                  defaultValue={loaderData.generationProject.ref_id}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/generation_project_ref_id"
                />
              </FormControl>
            </Stack>
          </CardContent>

          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
              >
                Change Generation Project
              </Button>
            </ButtonGroup>
          </CardActions>
        </Card>
      )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/push-integrations/slack-tasks",
  {
    error: () => `There was an error upserting Slack task settings! Please try again!`,
  }
);
