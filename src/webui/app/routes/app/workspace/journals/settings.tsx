import {
  RecurringTaskPeriod,
  ApiError,
  Difficulty,
  Eisen,
  WorkspaceFeature,
  JournalGenerationApproach,
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
  ToggleButtonGroup,
  ToggleButton,
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
    generationApproach: z.nativeEnum(JournalGenerationApproach),
    generationInAdvanceDaysForDaily: z.coerce.number().optional(),
    generationInAdvanceDaysForWeekly: z.coerce.number().optional(),
    generationInAdvanceDaysForMonthly: z.coerce.number().optional(),
    generationInAdvanceDaysForQuarterly: z.coerce.number().optional(),
    generationInAdvanceDaysForYearly: z.coerce.number().optional(),
    writingTaskProject: z.string().optional(),
    writingTaskEisen: z.nativeEnum(Eisen).optional(),
    writingTaskDifficulty: z.nativeEnum(Difficulty).optional(),
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

  const journalSettingsResponse = await apiClient.journals.journalLoadSettings(
    {},
  );

  return json({
    periods: journalSettingsResponse.periods,
    generationApproach: journalSettingsResponse.generation_approach,
    generationInAdvanceDays: journalSettingsResponse.generation_in_advance_days,
    writingTaskProject: journalSettingsResponse.writing_task_project,
    writingTaskGenParams: journalSettingsResponse.writing_task_gen_params,
    writingTasks: journalSettingsResponse.writing_tasks,
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

        await apiClient.journals.journalUpdateSettings({
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
          writing_task_project_ref_id: {
            should_change: true,
            value: form.writingTaskProject,
          },
          writing_task_eisen: {
            should_change: true,
            value: form.writingTaskEisen,
          },
          writing_task_difficulty: {
            should_change: true,
            value: form.writingTaskDifficulty,
          },
        });

        return redirect(`/app/workspace/journals/settings`);
      }

      case "regen": {
        await apiClient.journals.journalRegen({});
        return redirect(`/app/workspace/journals/settings`);
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

export default function JournalsSettings() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const isBigScreen = useBigScreen();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const [periods, setPeriods] = useState<RecurringTaskPeriod[]>(
    loaderData.periods,
  );

  const [approach, setApproach] = useState<JournalGenerationApproach>(
    loaderData.generationApproach,
  );

  const inputsEnabled = navigation.state === "idle";

  useEffect(() => {
    setPeriods(loaderData.periods);
    setApproach(loaderData.generationApproach);
  }, [loaderData]);

  return (
    <BranchPanel
      key={"journals/settings"}
      returnLocation="/app/workspace/journals"
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.JOURNALS,
      ) && (
        <>
          <SectionCard
            id="journals-settings"
            title="Settings"
            actions={
              <SectionActions
                id="journals-settings-actions"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  ActionSingle({
                    id: "journals-settings-save",
                    text: "Save",
                    value: "update",
                    highlight: true,
                  }),
                  ActionSingle({
                    id: "journals-settings-regen",
                    text: "Regen",
                    value: "regen",
                  }),
                ]}
              />
            }
          >
            <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
              <FormControl fullWidth>
                <FormLabel id="periods">Periods You Want To Journal</FormLabel>
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
                <ToggleButtonGroup
                  value={approach}
                  exclusive
                  fullWidth
                  onChange={(_, newApproach) =>
                    newApproach !== null && setApproach(newApproach)
                  }
                >
                  <ToggleButton
                    size="small"
                    id="approach-both"
                    disabled={!inputsEnabled}
                    value={JournalGenerationApproach.BOTH_JOURNAL_AND_TASK}
                  >
                    Both Journal and Task
                  </ToggleButton>
                  <ToggleButton
                    size="small"
                    id="approach-journal"
                    disabled={!inputsEnabled}
                    value={JournalGenerationApproach.ONLY_JOURNAL}
                  >
                    Only Journal
                  </ToggleButton>
                  <ToggleButton
                    size="small"
                    id="approach-none"
                    disabled={!inputsEnabled}
                    value={JournalGenerationApproach.NONE}
                  >
                    None
                  </ToggleButton>
                </ToggleButtonGroup>
                <input
                  name="generationApproach"
                  type="hidden"
                  value={approach}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/generation_approach"
                />
              </FormControl>
            </Stack>

            {approach === JournalGenerationApproach.BOTH_JOURNAL_AND_TASK && (
              <>
                <Divider>
                  <Typography variant="h6">Writing Task Properties</Typography>
                </Divider>

                <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
                  {isWorkspaceFeatureAvailable(
                    topLevelInfo.workspace,
                    WorkspaceFeature.PROJECTS,
                  ) && (
                    <FormControl fullWidth sx={{ alignSelf: "flex-end" }}>
                      <ProjectSelect
                        name="writingTaskProject"
                        label="Writing Task Project"
                        inputsEnabled={inputsEnabled}
                        disabled={false}
                        allProjects={loaderData.allProjects!}
                        defaultValue={loaderData.writingTaskProject?.ref_id}
                      />
                      <FieldError
                        actionResult={actionData}
                        fieldName="/writing_task_project_ref_id"
                      />
                    </FormControl>
                  )}

                  <FormControl fullWidth sx={{ alignSelf: "flex-end" }}>
                    <FormLabel id="writingTaskEisen">
                      Writing Task Eisen
                    </FormLabel>
                    <EisenhowerSelect
                      name="writingTaskEisen"
                      inputsEnabled={inputsEnabled}
                      defaultValue={
                        loaderData.writingTaskGenParams?.eisen ??
                        Eisen.IMPORTANT
                      }
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/writing_task_eisen"
                    />
                  </FormControl>

                  <FormControl fullWidth sx={{ alignSelf: "flex-end" }}>
                    <FormLabel id="writingTaskDifficulty">
                      Writing Task Difficulty
                    </FormLabel>
                    <DifficultySelect
                      name="writingTaskDifficulty"
                      inputsEnabled={inputsEnabled}
                      defaultValue={
                        loaderData.writingTaskGenParams?.difficulty ??
                        Difficulty.EASY
                      }
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/writing_task_difficulty"
                    />
                  </FormControl>
                </Stack>
              </>
            )}

            {(approach === JournalGenerationApproach.BOTH_JOURNAL_AND_TASK ||
              approach === JournalGenerationApproach.ONLY_JOURNAL) && (
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
          </SectionCard>

          <SectionCard
            id="journals-generated-journals-and-writing-tasks"
            title="Generated Writing Tasks"
          >
            <InboxTaskStack
              topLevelInfo={topLevelInfo}
              showOptions={{
                showStatus: true,
                showEisen: true,
                showDifficulty: true,
                showDueDate: true,
              }}
              inboxTasks={loaderData.writingTasks}
            />
          </SectionCard>
        </>
      )}
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/journals",
  ParamsSchema,
  {
    notFound: () => `Could not find the journals settings!`,
    error: () =>
      `There was an error loading the journals settings! Please try again!`,
  },
);
