import type { ProjectSummary } from "@jupiter/webapi-client";
import {
  ApiError,
  RecurringTaskPeriod,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
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
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("change-generation-period"),
    generationPeriod: z.nativeEnum(RecurringTaskPeriod),
  }),
  z.object({
    intent: z.literal("change-cleanup-project"),
    cleanupProject: z.string(),
  }),
]);

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

  const response = await getLoggedInApiClient(
    session
  ).workingMem.workingMemLoadSettings({});

  return json({
    generationPeriod: response.generation_period,
    cleanupProject: response.cleanup_project,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "change-generation-period": {
        await getLoggedInApiClient(
          session
        ).workingMem.workingMemChangeGenerationPeriod({
          generation_period: form.generationPeriod,
        });

        return redirect(`/workspace/working-mem/settings`);
      }

      case "change-cleanup-project": {
        await getLoggedInApiClient(
          session
        ).workingMem.workingMemChangeCleanUpProject({
          cleanup_project_ref_id: form.cleanupProject,
        });

        return redirect(`/workspace/working-mem/settings`);
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

export default function MetricsSettings() {
  const transition = useTransition();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel returnLocation="/workspace/working-mem">
      <Card>
        <GlobalError actionResult={actionData} />

        <CardHeader title="Clean Up Project" />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="generationPeriod">Generation Period</InputLabel>
              <Select
                labelId="status"
                name="generationPeriod"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.generationPeriod}
                label="Generation Period"
              >
                <MenuItem value={RecurringTaskPeriod.DAILY}>
                  {periodName(RecurringTaskPeriod.DAILY)}
                </MenuItem>
                <MenuItem value={RecurringTaskPeriod.WEEKLY}>
                  {periodName(RecurringTaskPeriod.WEEKLY)}
                </MenuItem>
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/generation_period"
              />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <FormControl fullWidth>
                <InputLabel id="cleanupProject">Clean Up Project</InputLabel>
                <Select
                  labelId="cleanupProject"
                  name="cleanupProject"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.cleanupProject.ref_id}
                  label="cleanup Project"
                >
                  {loaderData.allProjects.map((p) => (
                    <MenuItem key={p.ref_id} value={p.ref_id}>
                      {p.name}
                    </MenuItem>
                  ))}
                </Select>
                <FieldError
                  actionResult={actionData}
                  fieldName="/cleanup_project_ref_id"
                />
              </FormControl>
            )}
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="outlined"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="change-generation-period"
            >
              Change Generation Period
            </Button>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="change-cleanup-project"
              >
                Change Cleanup Project
              </Button>
            )}
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error upserting the working mem settings! Please try again!`
);
