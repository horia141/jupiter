import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import type { Project } from "jupiter-gen";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const UpdateFormSchema = {
  project: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_default_project: true,
    include_projects: true,
    });

  const slackTaskSettingsResponse = await getLoggedInApiClient(
    session
  ).slackTask.loadSlackTaskSettings({});

  return json({
    generationProject: slackTaskSettingsResponse.generation_project,
    defaultProject: summaryResponse.default_project as Project,
    allProjects: summaryResponse.projects as Array<Project>,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  try {
    await getLoggedInApiClient(
      session
    ).slackTask.changeSlackTaskGenerationProject({
      generation_project_ref_id: { the_id: form.project },
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

export default function SlackTasksSettings() {
  const transition = useTransition();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafCard returnLocation="/workspace/push-integrations/slack-tasks">
      <GlobalError actionResult={actionData} />
      <Card>
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="project">Project</InputLabel>
              <Select
                labelId="project"
                name="project"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.generationProject.ref_id.the_id}
                label="Project"
              >
                {loaderData.allProjects.map((p) => (
                  <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                    {p.name.the_name}
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
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Change Generation Project
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error upserting Slack task settings! Please try again!`
);
