import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import type { ProjectSummary } from "@jupiter/webapi-client";
import { ApiError, WorkspaceFeature } from "@jupiter/webapi-client";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const UpdateFormSchema = {
  project: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
  });

  const slackTaskSettingsResponse = await getLoggedInApiClient(
    session
  ).pushIntegrations.slackTaskLoadSettings({});

  return json({
    generationProject: slackTaskSettingsResponse.generation_project,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  try {
    if (form.project === undefined) {
      throw new Error("Invalid application state");
    }

    await getLoggedInApiClient(
      session
    ).pushIntegrations.slackTaskChangeGenerationProject({
      generation_project_ref_id: form.project,
    });

    return redirect(`/workspace/push-integrations/slack-tasks/settings`);
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
  const transition = useTransition();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel returnLocation="/workspace/push-integrations/slack-tasks">
      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.PROJECTS
      ) && (
        <Card>
          <GlobalError actionResult={actionData} />

          <CardHeader title="Generation Project" />
          <CardContent>
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="project">Project</InputLabel>
                <Select
                  labelId="project"
                  name="project"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.generationProject.ref_id}
                  label="Project"
                >
                  {loaderData.allProjects.map((p) => (
                    <MenuItem key={p.ref_id} value={p.ref_id}>
                      {p.name}
                    </MenuItem>
                  ))}
                </Select>
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error upserting Slack task settings! Please try again!`
);
