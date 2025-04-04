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
  FormLabel,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
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
import { PeriodSelect } from "~/components/period-select";
import { ProjectSelect } from "~/components/project-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
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

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  const response = await apiClient.workingMem.workingMemLoadSettings({});

  return json({
    generationPeriod: response.generation_period,
    cleanupProject: response.cleanup_project,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "change-generation-period": {
        await apiClient.workingMem.workingMemChangeGenerationPeriod({
          generation_period: form.generationPeriod,
        });

        return redirect(`/app/workspace/working-mem/settings`);
      }

      case "change-cleanup-project": {
        await apiClient.workingMem.workingMemChangeCleanUpProject({
          cleanup_project_ref_id: form.cleanupProject,
        });

        return redirect(`/app/workspace/working-mem/settings`);
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
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={"working-mem/settings"}
      returnLocation="/app/workspace/working-mem"
      inputsEnabled={inputsEnabled}
    >
      <Card>
        <GlobalError actionResult={actionData} />

        <CardHeader title="Clean Up Project" />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <FormLabel id="generationPeriod">Generation Period</FormLabel>
              <PeriodSelect
                labelId="generationPeriod"
                label="Generation Period"
                name="generationPeriod"
                inputsEnabled={inputsEnabled}
                defaultValue={loaderData.generationPeriod}
                allowedValues={[
                  RecurringTaskPeriod.DAILY,
                  RecurringTaskPeriod.WEEKLY,
                ]}
              />
              <FieldError
                actionResult={actionData}
                fieldName="/generation_period"
              />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS,
            ) && (
              <FormControl fullWidth>
                <ProjectSelect
                  name="cleanupProject"
                  label="Clean Up Project"
                  inputsEnabled={inputsEnabled}
                  allProjects={loaderData.allProjects}
                  disabled={false}
                  defaultValue={loaderData.cleanupProject.ref_id}
                />
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
              WorkspaceFeature.PROJECTS,
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

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/working-mem",
  {
    error: () =>
      `There was an error upserting the working mem settings! Please try again!`,
  },
);
