import type { InboxTask, Project } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  HabitRepeatsStrategy,
  InboxTaskStatus,
  NoteDomain,
  RecurringTaskPeriod,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
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
import {
  useActionData,
  useFetcher,
  useNavigation,
  useSearchParams,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/infra/entity-note-editor";
import { HabitRepeatStrategySelect } from "~/components/domain/concept/habit/habit-repeat-strategy-select";
import { HabitStreakCalendar } from "~/components/domain/concept/habit/habit-streak-calendar";
import { InboxTaskStack } from "~/components/domain/concept/inbox-task/inbox-task-stack";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/domain/concept/project/project-select";
import { RecurringTaskGenParamsBlock } from "~/components/domain/core/recurring-task-gen-params-block";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { newURLParams } from "~/logic/domain/navigation";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { IsKeySelect } from "~/components/domain/core/is-key-select";

const ParamsSchema = z.object({
  id: z.string(),
});

const QuerySchema = z.object({
  inboxTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
  includeStreakMarksForYear: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    project: z.string().optional(),
    period: z.nativeEnum(RecurringTaskPeriod),
    isKey: CheckboxAsString,
    eisen: z.nativeEnum(Eisen),
    difficulty: z.nativeEnum(Difficulty),
    actionableFromDay: z.string().optional(),
    actionableFromMonth: z.string().optional(),
    dueAtDay: z.string().optional(),
    dueAtMonth: z.string().optional(),
    skipRule: z.string().optional(),
    repeatsStrategy: z
      .nativeEnum(HabitRepeatsStrategy)
      .or(z.literal("none"))
      .optional(),
    repeatsInPeriodCount: z.string().optional(),
  }),
  z.object({
    intent: z.literal("regen"),
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
  const query = parseQuery(request, QuerySchema); // Parse the query parameters

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const result = await apiClient.habits.habitLoad({
      ref_id: id,
      allow_archived: true,
      inbox_task_retrieve_offset: query.inboxTasksRetrieveOffset, // Pass the offset to the API call
      include_streak_marks_for_year: query.includeStreakMarksForYear,
    });

    return json({
      habit: result.habit,
      note: result.note,
      streakMarks: result.streak_marks,
      streakMarkYear: result.streak_mark_year,
      project: result.project,
      inboxTasks: result.inbox_tasks,
      inboxTasksTotalCnt: result.inbox_tasks_total_cnt,
      inboxTasksPageSize: result.inbox_tasks_page_size,
      allProjects: summaryResponse.projects as Array<Project>,
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
        await apiClient.habits.habitUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          project_ref_id: {
            should_change: form.project ? true : false,
            value: form.project,
          },
          period: {
            should_change: true,
            value: form.period,
          },
          is_key: {
            should_change: true,
            value: form.isKey,
          },
          eisen: {
            should_change: true,
            value: form.eisen,
          },
          difficulty: {
            should_change: true,
            value: form.difficulty,
          },
          actionable_from_day: {
            should_change: true,
            value:
              form.actionableFromDay === undefined ||
              form.actionableFromDay === ""
                ? undefined
                : parseInt(form.actionableFromDay),
          },
          actionable_from_month: {
            should_change: true,
            value:
              form.actionableFromMonth === undefined ||
              form.actionableFromMonth === ""
                ? undefined
                : parseInt(form.actionableFromMonth),
          },
          due_at_day: {
            should_change: true,
            value:
              form.dueAtDay === undefined || form.dueAtDay === ""
                ? undefined
                : parseInt(form.dueAtDay),
          },
          due_at_month: {
            should_change: true,
            value:
              form.dueAtMonth === undefined || form.dueAtMonth === ""
                ? undefined
                : parseInt(form.dueAtMonth),
          },
          skip_rule: {
            should_change: true,
            value:
              form.skipRule === undefined || form.skipRule === ""
                ? undefined
                : form.skipRule,
          },
          repeats_strategy: {
            should_change: true,
            value:
              form.repeatsStrategy !== undefined &&
              form.repeatsStrategy !== "none"
                ? form.repeatsStrategy
                : undefined,
          },
          repeats_in_period_count: {
            should_change: true,
            value: form.repeatsInPeriodCount
              ? parseInt(form.repeatsInPeriodCount)
              : undefined,
          },
        });

        return redirect(`/app/workspace/habits`);
      }

      case "regen": {
        await apiClient.habits.habitRegen({
          ref_id: id,
        });

        return redirect(`/app/workspace/habits/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.HABIT,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/habits/${id}`);
      }

      case "archive": {
        await apiClient.habits.habitArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/habits`);
      }

      case "remove": {
        await apiClient.habits.habitRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/habits`);
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

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function Habit() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const [query] = useSearchParams();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.habit.archived;

  const [selectedProject, setSelectedProject] = useState(
    loaderData.project.ref_id,
  );

  const [selectedPeriod, setSelectedPeriod] = useState(
    loaderData.habit.gen_params.period,
  );

  const [selectedRepeatsStrategy, setSelectedRepeatsStrategy] = useState<
    HabitRepeatsStrategy | "none"
  >(loaderData.habit.repeats_strategy || "none");

  const sortedInboxTasks = sortInboxTasksNaturally(loaderData.inboxTasks, {
    dueDateAscending: false,
  });

  const cardActionFetcher = useFetcher();

  function handleCardMarkDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.DONE,
      },
      {
        method: "post",
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  function handleCardMarkNotDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  useEffect(() => {
    // Update states based on loader data. This is necessary because these
    // two are not otherwise updated when the loader data changes. Which happens
    // on a navigation event.
    setSelectedProject(loaderData.project.ref_id);
    setSelectedPeriod(loaderData.habit.gen_params.period);
    setSelectedRepeatsStrategy(loaderData.habit.repeats_strategy || "none");
  }, [loaderData]);

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`habit-${loaderData.habit.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.habit.archived}
      returnLocation="/app/workspace/habits"
      initialExpansionState={LeafPanelExpansionState.MEDIUM}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <Stack direction="row" useFlexGap spacing={1}>
              <FormControl sx={{ flexGrow: 3 }}>
                <InputLabel id="name">Name</InputLabel>
                <OutlinedInput
                  label="Name"
                  name="name"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.habit.name}
                />
                <FieldError actionResult={actionData} fieldName="/name" />
              </FormControl>

              <FormControl sx={{ flexGrow: 1 }}>
                <IsKeySelect
                  name="isKey"
                  defaultValue={loaderData.habit.is_key}
                />
                <FieldError actionResult={actionData} fieldName="/is_key" />
              </FormControl>
            </Stack>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS,
            ) && (
              <FormControl fullWidth>
                <ProjectSelect
                  name="project"
                  label="Project"
                  inputsEnabled={inputsEnabled}
                  disabled={!inputsEnabled}
                  allProjects={loaderData.allProjects}
                  value={selectedProject}
                  onChange={setSelectedProject}
                />
                <FieldError actionResult={actionData} fieldName="/project" />
              </FormControl>
            )}

            <RecurringTaskGenParamsBlock
              allowSkipRule
              inputsEnabled={inputsEnabled}
              period={selectedPeriod}
              onChangePeriod={(newPeriod) => {
                if (newPeriod === "none") {
                  setSelectedPeriod(RecurringTaskPeriod.DAILY);
                } else {
                  setSelectedPeriod(newPeriod);
                }
              }}
              eisen={loaderData.habit.gen_params.eisen}
              difficulty={loaderData.habit.gen_params.difficulty}
              actionableFromDay={
                loaderData.habit.gen_params.actionable_from_day
              }
              actionableFromMonth={
                loaderData.habit.gen_params.actionable_from_month
              }
              dueAtDay={loaderData.habit.gen_params.due_at_day}
              dueAtMonth={loaderData.habit.gen_params.due_at_month}
              skipRule={loaderData.habit.gen_params.skip_rule}
              actionData={actionData}
            />

            {selectedPeriod !== RecurringTaskPeriod.DAILY && (
              <Stack direction="row" spacing={2}>
                <FormControl sx={{ flexGrow: 3 }}>
                  <HabitRepeatStrategySelect
                    name="repeatsStrategy"
                    inputsEnabled={inputsEnabled}
                    allowNone
                    value={selectedRepeatsStrategy}
                    onChange={(newStrategy) =>
                      setSelectedRepeatsStrategy(newStrategy)
                    }
                  />
                </FormControl>

                {selectedRepeatsStrategy !== "none" && (
                  <FormControl sx={{ flexGrow: 1 }}>
                    <InputLabel id="repeatsInPeriodCount">
                      Repeats In Period [Optional]
                    </InputLabel>
                    <OutlinedInput
                      label="Repeats In Period"
                      name="repeatsInPeriodCount"
                      readOnly={!inputsEnabled}
                      defaultValue={loaderData.habit.repeats_in_period_count}
                      sx={{ height: "100%" }}
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/repeats_in_period_count"
                    />
                  </FormControl>
                )}
              </Stack>
            )}
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>
            <Button
              variant="outlined"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="regen"
            >
              Regen
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      <Card>
        <CardContent>
          <HabitStreakCalendar
            year={loaderData.streakMarkYear}
            currentYear={today.year}
            habit={loaderData.habit}
            streakMarks={loaderData.streakMarks}
            inboxTasks={sortedInboxTasks}
            getYearUrl={(year) =>
              `/app/workspace/habits/${loaderData.habit.ref_id}?${newURLParams(
                query,
                "includeStreakMarksForYear",
                year.toString(),
              )}`
            }
          />
        </CardContent>
      </Card>

      <Card>
        {!loaderData.note && (
          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>

      {sortedInboxTasks.length > 0 && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Inbox Tasks"
          inboxTasks={sortedInboxTasks}
          withPages={{
            retrieveOffsetParamName: "inboxTasksRetrieveOffset",
            totalCnt: loaderData.inboxTasksTotalCnt,
            pageSize: loaderData.inboxTasksPageSize,
          }}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/habits",
  ParamsSchema,
  {
    notFound: (params) => `Could not find habit with ID ${params.id}!`,
    error: (params) =>
      `There was an error loading habit with ID ${params.id}! Please try again!`,
  },
);
