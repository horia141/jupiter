import { ProjectSummary, RecurringTaskPeriod ,
  ApiError,
  Difficulty,
  Eisen,
  WorkspaceFeature,
  TimePlanGenerationApproach,
} from "@jupiter/webapi-client";
import { z } from "zod";
import { ActionFunctionArgs, json, LoaderFunctionArgs } from "@remix-run/node";
import { parseForm } from "zodix";
import { StatusCodes } from "http-status-codes";
import {
  Form,
  ShouldRevalidateFunction,
  useActionData,
  useNavigation,
} from "@remix-run/react";
import { useContext, useEffect, useState } from "react";
import {
  Card,
  CardContent,
  Stack,
  FormControl,
  CardHeader,
  FormLabel,
  Button,
  ButtonGroup,
  CardActions,
} from "@mui/material";

import { DisplayType } from "~/rendering/use-nested-entities";
import { getLoggedInApiClient } from "~/api-clients.server";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { TopLevelInfoContext } from "~/top-level-context";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { FieldError, GlobalError } from "~/components/infra/errors";
import {
  makeBranchErrorBoundary,
} from "~/components/infra/error-boundary";
import { PeriodSelect } from "~/components/period-select";
import { ProjectSelect } from "~/components/project-select";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { DifficultySelect } from "~/components/difficulty-select";
import {
  selectZod,
  fixSelectOutputToEnumStrict,
} from "~/logic/select";
import { useBigScreen } from "~/rendering/use-big-screen";
import { TimePlanGenerationApproachSelect } from "~/components/time-plan-generation-approach-select";

const ParamsSchema = z.object({});

const UpdateFormSchema = z.object({
  periods: selectZod(z.nativeEnum(RecurringTaskPeriod)),
  generationApproach: z.nativeEnum(TimePlanGenerationApproach),
  planningTaskProject: z.string().optional(),
  planningTaskEisen: z.nativeEnum(Eisen).optional(),
  planningTaskDifficulty: z.nativeEnum(Difficulty).optional(),
});

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_workspace: true,
    include_projects: true,
  });

  const timePlanSettingsResponse =
    await apiClient.timePlans.timePlanLoadSettings({});

  return json({
    periods: timePlanSettingsResponse.periods,
    generationApproach: timePlanSettingsResponse.generation_approach,
    planningTaskProject: timePlanSettingsResponse.planning_task_project,
    planningTaskGenParams: timePlanSettingsResponse.planning_task_gen_params,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    await apiClient.timePlans.timePlanUpdateSettings({
      periods: {
        should_change: true,
        value: fixSelectOutputToEnumStrict<RecurringTaskPeriod>(form.periods),
      },
      generation_approach: {
        should_change: true,
        value: form.generationApproach,
      },
      planning_task_project_ref_id: {
        should_change: true,
        value: form.planningTaskProject,
      },
      planning_task_eisen: {
        should_change: true,
        value: form.planningTaskEisen,
      },
      planning_task_difficulty: {
        should_change: true,
        value: form.planningTaskDifficulty,
      },
    });

    return json(noErrorNoData());
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

export default function TimePlansSettings() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const isBigScreen = useBigScreen();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const [approach, setApproach] = useState<TimePlanGenerationApproach>(
    loaderData.generationApproach
  );

  const inputsEnabled = navigation.state === "idle";

  useEffect(() => {
    setApproach(loaderData.generationApproach);
  }, [loaderData.generationApproach]);

  return (
    <BranchPanel
      key={"time-plans/settings"}
      returnLocation="/app/workspace/time-plans"
      inputsEnabled={inputsEnabled}
    >
      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.TIME_PLANS,
      ) && (
        <Form method="post">
          <Card>
            <GlobalError actionResult={actionData} />

            <CardHeader title="Settings" />
            <CardContent>
              <Stack spacing={2} useFlexGap>
                <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
                  <FormControl fullWidth>
                    <FormLabel id="periods">Periods You Want To Plan</FormLabel>
                    <PeriodSelect
                      labelId="periods"
                      label="Periods"
                      name="periods"
                      multiSelect
                      inputsEnabled={inputsEnabled}
                      defaultValue={loaderData.periods}
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/periods"
                    />
                  </FormControl>

                  <FormControl fullWidth>
                    <FormLabel id="generationApproach">
                      Generation Approach
                    </FormLabel>
                    <TimePlanGenerationApproachSelect
                      name="generationApproach"
                      inputsEnabled={inputsEnabled}
                      value={approach}
                      onChange={setApproach}
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/generation_approach"
                    />
                  </FormControl>

                </Stack>

                {approach === TimePlanGenerationApproach.BOTH_PLAN_AND_TASK && (
                  <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
                  {isWorkspaceFeatureAvailable(
                    topLevelInfo.workspace,
                    WorkspaceFeature.PROJECTS,
                  ) && (
                    <FormControl fullWidth sx={{ alignSelf: "flex-end" }}>
                      <ProjectSelect
                        name="planningTaskProject"
                        label="Planning Task Project"
                        inputsEnabled={inputsEnabled}
                        disabled={false}
                        allProjects={loaderData.allProjects}
                        defaultValue={loaderData.planningTaskProject?.ref_id}
                      />
                      <FieldError
                        actionResult={actionData}
                        fieldName="/planning_task_project_ref_id"
                      />
                    </FormControl>
                  )}

                  <FormControl fullWidth sx={{ alignSelf: "flex-end" }}>
                    <FormLabel id="planningTaskEisen">
                      Planning Task Eisen
                    </FormLabel>
                    <EisenhowerSelect
                      name="planningTaskEisen"
                      inputsEnabled={inputsEnabled}
                      defaultValue={loaderData.planningTaskGenParams?.eisen ?? Eisen.IMPORTANT}
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/planning_task_eisen"
                    />
                  </FormControl>

                  <FormControl fullWidth sx={{ alignSelf: "flex-end" }}>
                    <FormLabel id="planningTaskDifficulty">
                      Planning Task Difficulty
                    </FormLabel>
                    <DifficultySelect
                      name="planningTaskDifficulty"
                      inputsEnabled={inputsEnabled}
                      defaultValue={loaderData.planningTaskGenParams?.difficulty ?? Difficulty.EASY}
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/planning_task_difficulty"
                    />
                    </FormControl>
                  </Stack>
                )}
              </Stack>
            </CardContent>

            <CardActions>
              <ButtonGroup>
                <Button
                  variant="contained"
                  type="submit"
                  disabled={!inputsEnabled}
                >
                  Save
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>
        </Form>
      )}
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/time-plans",
  ParamsSchema,
  {
    notFound: () => `Could not find the time plans settings!`,
    error: () =>
      `There was an error loading the time plans settings! Please try again!`,
  },
);
