import {
  RecurringTaskPeriod,
  ApiError,
  Difficulty,
  Eisen,
  WorkspaceFeature,
  TimePlanGenerationApproach,
} from "@jupiter/webapi-client";
import { z } from "zod";
import {
  ActionFunctionArgs,
  json,
  LoaderFunctionArgs,
  redirect,
} from "@remix-run/node";
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
  Stack,
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Divider,
  Typography,
} from "@mui/material";

import { DisplayType } from "~/rendering/use-nested-entities";
import { getLoggedInApiClient } from "~/api-clients.server";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { TopLevelInfoContext } from "~/top-level-context";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { PeriodSelect } from "~/components/domain/core/period-select";
import { ProjectSelect } from "~/components/domain/concept/project/project-select";
import { EisenhowerSelect } from "~/components/domain/core/eisenhower-select";
import { DifficultySelect } from "~/components/domain/core/difficulty-select";
import { selectZod, fixSelectOutputToEnumStrict } from "~/logic/select";
import { useBigScreen } from "~/rendering/use-big-screen";
import { TimePlanGenerationApproachSelect } from "~/components/domain/concept/time-plan/time-plan-generation-approach-select";
import { periodName } from "~/logic/domain/period";
import { SectionCard } from "~/components/infra/section-card";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { InboxTaskStack } from "~/components/domain/concept/inbox-task/inbox-task-stack";

const ParamsSchema = z.object({});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    periods: selectZod(z.nativeEnum(RecurringTaskPeriod)),
    generationApproach: z.nativeEnum(TimePlanGenerationApproach),
    generationInAdvanceDaysForDaily: z.coerce.number().optional(),
    generationInAdvanceDaysForWeekly: z.coerce.number().optional(),
    generationInAdvanceDaysForMonthly: z.coerce.number().optional(),
    generationInAdvanceDaysForQuarterly: z.coerce.number().optional(),
    generationInAdvanceDaysForYearly: z.coerce.number().optional(),
    planningTaskProject: z.string().optional(),
    planningTaskEisen: z.nativeEnum(Eisen).optional(),
    planningTaskDifficulty: z.nativeEnum(Difficulty).optional(),
  }),
  z.object({
    intent: z.literal("regen"),
  }),
]);

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
    generationInAdvanceDays:
      timePlanSettingsResponse.generation_in_advance_days,
    planningTaskProject: timePlanSettingsResponse.planning_task_project,
    planningTaskGenParams: timePlanSettingsResponse.planning_task_gen_params,
    planningTasks: timePlanSettingsResponse.planning_tasks,
    allProjects: summaryResponse.projects || undefined,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        const generationInAdvanceDays: Record<string, number> = {};
        if (form.generationInAdvanceDaysForDaily !== undefined) {
          generationInAdvanceDays[RecurringTaskPeriod.DAILY] =
            form.generationInAdvanceDaysForDaily;
        }
        if (form.generationInAdvanceDaysForWeekly !== undefined) {
          generationInAdvanceDays[RecurringTaskPeriod.WEEKLY] =
            form.generationInAdvanceDaysForWeekly;
        }
        if (form.generationInAdvanceDaysForMonthly !== undefined) {
          generationInAdvanceDays[RecurringTaskPeriod.MONTHLY] =
            form.generationInAdvanceDaysForMonthly;
        }
        if (form.generationInAdvanceDaysForQuarterly !== undefined) {
          generationInAdvanceDays[RecurringTaskPeriod.QUARTERLY] =
            form.generationInAdvanceDaysForQuarterly;
        }
        if (form.generationInAdvanceDaysForYearly !== undefined) {
          generationInAdvanceDays[RecurringTaskPeriod.YEARLY] =
            form.generationInAdvanceDaysForYearly;
        }

        await apiClient.timePlans.timePlanUpdateSettings({
          periods: {
            should_change: true,
            value: fixSelectOutputToEnumStrict<RecurringTaskPeriod>(
              form.periods,
            ),
          },
          generation_approach: {
            should_change: true,
            value: form.generationApproach,
          },
          generation_in_advance_days: {
            should_change: true,
            value: generationInAdvanceDays,
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

        return redirect(`/app/workspace/time-plans/settings`);
      }

      case "regen": {
        await apiClient.timePlans.timePlanRegen({});
        return redirect(`/app/workspace/time-plans/settings`);
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

export default function TimePlansSettings() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const isBigScreen = useBigScreen();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const [periods, setPeriods] = useState<RecurringTaskPeriod[]>(
    loaderData.periods,
  );

  const [approach, setApproach] = useState<TimePlanGenerationApproach>(
    loaderData.generationApproach,
  );

  const inputsEnabled = navigation.state === "idle";

  useEffect(() => {
    setPeriods(loaderData.periods);
    setApproach(loaderData.generationApproach);
  }, [loaderData]);

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
          <SectionCard
            id="time-plans-settings"
            title="Settings"
            actions={
              <SectionActions
                id="time-plans-settings-actions"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  ActionSingle({
                    id: "time-plans-settings-save",
                    text: "Save",
                    value: "update",
                    highlight: true,
                  }),
                  ActionSingle({
                    id: "time-plans-settings-regen",
                    text: "Regen",
                    value: "regen",
                  }),
                ]}
              />
            }
          >
            <GlobalError actionResult={actionData} />
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
                    value={periods}
                    onChange={(newPeriods) => {
                      setPeriods(newPeriods as RecurringTaskPeriod[]);
                    }}
                  />
                  <FieldError actionResult={actionData} fieldName="/periods" />
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
                <>
                  <Divider>
                    <Typography variant="h6">
                      Planning Inbox Task Properties
                    </Typography>
                  </Divider>

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
                          allProjects={loaderData.allProjects!}
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
                        defaultValue={
                          loaderData.planningTaskGenParams?.eisen ??
                          Eisen.IMPORTANT
                        }
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
                        defaultValue={
                          loaderData.planningTaskGenParams?.difficulty ??
                          Difficulty.EASY
                        }
                      />
                      <FieldError
                        actionResult={actionData}
                        fieldName="/planning_task_difficulty"
                      />
                    </FormControl>
                  </Stack>
                </>
              )}

              {(approach === TimePlanGenerationApproach.BOTH_PLAN_AND_TASK ||
                approach === TimePlanGenerationApproach.ONLY_PLAN) && (
                <>
                  <Divider>
                    <Typography variant="h6">
                      Days To Generate In Advance
                    </Typography>
                  </Divider>

                  <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
                    {Object.values(RecurringTaskPeriod).map((period) => {
                      if (!periods.includes(period)) {
                        return null;
                      }

                      return (
                        <FormControl fullWidth key={period}>
                          <InputLabel
                            id={`generationInAdvanceDaysFor${period.charAt(0).toUpperCase() + period.slice(1)}`}
                          >
                            For {periodName(period)}
                          </InputLabel>
                          <OutlinedInput
                            name={`generationInAdvanceDaysFor${period.charAt(0).toUpperCase() + period.slice(1)}`}
                            label={`For ${periodName(period)}`}
                            disabled={!inputsEnabled}
                            defaultValue={
                              loaderData.generationInAdvanceDays[period] ?? 1
                            }
                          />
                          <FieldError
                            actionResult={actionData}
                            fieldName={`/generation_in_advance_days`}
                          />
                        </FormControl>
                      );
                    })}
                  </Stack>
                </>
              )}
            </Stack>
          </SectionCard>

          <SectionCard
            id="time-plans-generated-time-plans-and-planning-tasks"
            title="Generated Planning Tasks"
          >
            <InboxTaskStack
              topLevelInfo={topLevelInfo}
              showOptions={{
                showStatus: true,
                showEisen: true,
                showDifficulty: true,
                showDueDate: true,
              }}
              inboxTasks={loaderData.planningTasks}
            />
          </SectionCard>
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
