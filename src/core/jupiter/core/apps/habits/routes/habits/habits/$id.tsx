import type {
  AspectSummary,
  ChapterSummary,
  Contact,
  GoalSummary,
  HabitStack,
  InboxTask,
  LifePlan,
  MilestoneSummary,
} from "@jupiter/webapi-client";
import {
  NamedEntityTag,
  Difficulty,
  Eisen,
  HabitRepeatsStrategy,
  InboxTaskStatus,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import type {
  ActionFunctionArgs,
  LoaderFunctionArgs,
  ShouldRevalidateFunction,
} from "react-router";
import {
  redirect,
  useActionData,
  useFetcher,
  useNavigation,
  useSearchParams,
} from "react-router";
import { useContext } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams, parseQuery } from "zodix";
import { DateTime } from "luxon";

import { isWorkspaceFeatureAvailable } from "#/core/workspaces/root";
import {
  sortInboxTaskTimeEventsNaturally,
  timeEventInDayBlockToTimezone,
} from "#/core/common/sub/time_events/time-event";
import { TimeEventInDayBlockStack } from "#/core/common/sub/time_events/sub/in_day_block/component/stack";
import {
  sortInboxTasksNaturally,
  type InboxTaskParent,
} from "#/core/common/sub/inbox_tasks/root";
import { EntityNoteEditor } from "#/core/infra/component/entity-note-editor";
import { HabitPropertiesEditor } from "#/core/apps/habits/component/properties-editor";
import { HabitStreakCalendar } from "#/core/apps/habits/component/streak-calendar";
import { StreakInactivePeriodStack } from "#/core/apps/habits/sub/streak_inactive_period/component/stack";
import { InboxTaskStack } from "#/core/common/sub/inbox_tasks/component/stack";
import { makeLeafErrorBoundary } from "#/core/infra/component/error-boundary";
import { GlobalError } from "#/core/infra/component/errors";
import { LeafPanel } from "#/core/infra/component/layout/leaf-panel";
import { NestedOutlet } from "#/core/infra/component/layout/nested-outlet";
import { NestingAwareBlock } from "#/core/infra/component/layout/nesting-aware-block";
import { LeafPanelExpansionState } from "#/core/infra/leaf-panel-expansion";
import {
  DisplayType,
  useLeafNeedsToShowLeaflet,
} from "#/core/infra/component/use-nested-entities";
import { TopLevelInfoContext } from "#/core/infra/top-level-context";
import {
  SectionActions,
  ActionSingle,
  NavSingle,
} from "#/core/infra/component/section-actions";
import { SectionCard } from "#/core/infra/component/section-card";
import { TimePlanActivityList } from "#/core/apps/time_plans/sub/activity/component/list";
import { noteStdOwner } from "#/core/common/sub/notes/note-std-owner";
import {
  handleActionApiError,
  handleLoaderApiError,
} from "#/core/infra/errors.server";
import { accessStatusAllowsWriterOrAbove } from "#/core/common/sub/access/access-level";
import {
  SchedulingParamsFormFields,
  schedulingParamsUpdateArgs,
} from "#/core/common/scheduling-params-form";
import { useLoaderDataSafeForAnimation } from "#/core/infra/component/use-loader-data-for-animation";
import { basicShouldRevalidate } from "#/core/infra/should-revalidate";
import { newURLParams } from "#/core/infra/navigation";
import { getLoggedInApiClient } from "#/core/infra/api-clients.server";

const ParamsSchema = z.object({
  id: z.string(),
});

const QuerySchema = z.object({
  inboxTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
  viewOneIncludeStreakMarksEarliestDate: z.string().optional(),
  viewOneIncludeStreakMarksLatestDate: z.string().optional(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    aspect: z.string().optional(),
    chapter: z.string().optional(),
    goal: z.string().optional(),
    isKey: CheckboxAsString,
    eisen: z.nativeEnum(Eisen),
    difficulty: z.nativeEnum(Difficulty),
    actionableFromDay: z.string().optional(),
    actionableFromMonth: z.string().optional(),
    dueAtDay: z.string().optional(),
    dueAtMonth: z.string().optional(),
    skipRule: z.string().optional(),
    stack: z.string().optional(),
    repeatsStrategy: z
      .nativeEnum(HabitRepeatsStrategy)
      .or(z.literal("none"))
      .optional(),
    repeatsInPeriodCount: z.string().optional(),
    suspended: CheckboxAsString,
    ...SchedulingParamsFormFields,
  }),
  z.object({
    intent: z.literal("gen"),
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
  z.object({
    intent: z.literal("create-publish"),
    publishOwner: z.string(),
  }),
  z.object({
    intent: z.literal("activate-publish"),
    publishEntityRefId: z.string(),
  }),
  z.object({
    intent: z.literal("to-draft-publish"),
    publishEntityRefId: z.string(),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const query = parseQuery(request, QuerySchema); // Parse the query parameters

  let earliestDate = query.viewOneIncludeStreakMarksEarliestDate;
  let latestDate = query.viewOneIncludeStreakMarksLatestDate;
  if (earliestDate === undefined) {
    earliestDate = DateTime.now().minus({ days: 90 }).toISODate();
    latestDate = DateTime.now().toISODate();
  }

  try {
    const summaryPromise = apiClient.application.getSummaries({
      include_workspace: true,
      include_life_plan: true,
      include_aspects: true,
      include_chapters: true,
      include_goals: true,
      include_milestones: true,
    });
    // Only this call depends on another one (the workspace's features), so it
    // chains off the summaries while everything else runs concurrently.
    const timePlanActivitiesPromise = summaryPromise.then(
      async (summaryResponse) => {
        if (
          !isWorkspaceFeatureAvailable(
            summaryResponse.workspace!,
            WorkspaceFeature.TIME_PLANS,
          )
        ) {
          return undefined;
        }
        const timePlanActivitiesResult =
          await apiClient.timePlans.timePlanActivityFindForTarget({
            allow_archived: true,
            target: `Habit:std:${id}`,
          });
        return timePlanActivitiesResult.entries;
      },
    );

    const [
      summaryResponse,
      allTags,
      allContacts,
      stacksResponse,
      result,
      timePlanActivities,
    ] = await Promise.all([
      summaryPromise,
      apiClient.tags.tagFind({
        allow_archived: false,
      }),
      apiClient.contacts.contactFind({
        allow_archived: false,
      }),
      apiClient.habits.habitStackFind({
        allow_archived: false,
        include_tags: false,
        include_notes: false,
        include_life_plan: false,
        include_habits: false,
      }),
      apiClient.habits.habitLoad({
        ref_id: id,
        allow_archived: true,
        inbox_task_retrieve_offset: query.inboxTasksRetrieveOffset, // Pass the offset to the API call
        include_streak_marks_earliest_date: earliestDate,
        include_streak_marks_latest_date: latestDate,
      }),
      timePlanActivitiesPromise,
    ]);

    return {
      habit: result.habit,
      tags: result.tags,
      note: result.note,
      streakMarks: result.streak_marks,
      streakMarkEarliestDate: result.streak_mark_earliest_date,
      streakMarkLatestDate: result.streak_mark_latest_date,
      streakInactivePeriods: result.streak_inactive_periods,
      aspect: result.aspect,
      chapter: result.chapter,
      goal: result.goal,
      inboxTasks: result.inbox_tasks,
      inboxTasksTotalCnt: result.inbox_tasks_total_cnt,
      inboxTasksPageSize: result.inbox_tasks_page_size,
      lifePlan: summaryResponse.life_plan as LifePlan | null,
      allAspects: summaryResponse.aspects as Array<AspectSummary> | null,
      allChapters: summaryResponse.chapters as Array<ChapterSummary> | null,
      allGoals: summaryResponse.goals as Array<GoalSummary> | null,
      allMilestones:
        summaryResponse.milestones as Array<MilestoneSummary> | null,
      allTags: allTags.tags,
      contacts:
        (
          result as {
            contacts?: Array<Contact>;
          }
        ).contacts ?? [],
      location: result.location ?? null,
      allContacts: allContacts.contacts as Array<Contact>,
      allStacks: mergeCurrentStack(
        stacksResponse.entries.map((entry) => entry.habit_stack),
        result.stack ?? null,
      ),
      timeEventBlocks: result.time_event_blocks,
      publishEntity: result.publish_entity ?? null,
      owner: result.owner,
      accessStatus: result.access_status ?? null,
      timePlanActivities,
    };
  } catch (error) {
    handleLoaderApiError(error);
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
          aspect_ref_id:
            form.aspect !== undefined
              ? { should_change: true, value: form.aspect }
              : { should_change: false },
          chapter_ref_id:
            form.aspect !== undefined
              ? {
                  should_change: true,
                  value:
                    form.chapter !== undefined && form.chapter !== ""
                      ? form.chapter
                      : undefined,
                }
              : { should_change: false },
          goal_ref_id:
            form.aspect !== undefined
              ? {
                  should_change: true,
                  value:
                    form.goal !== undefined && form.goal !== ""
                      ? form.goal
                      : undefined,
                }
              : { should_change: false },
          stack_ref_id: {
            should_change: true,
            value:
              form.stack !== undefined && form.stack !== "" ? form.stack : null,
          },
          is_key: {
            should_change: true,
            value: form.isKey,
          },
          suspended: {
            should_change: true,
            value: form.suspended,
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
          ...schedulingParamsUpdateArgs(form),
        });

        return redirect(`/app/workspace/apps/habits/habits`);
      }

      case "gen": {
        await apiClient.habits.habitRegen({
          ref_id: id,
        });

        return redirect(`/app/workspace/apps/habits/habits/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          owner: noteStdOwner(NamedEntityTag.HABIT, id),
          content: [],
        });

        return redirect(`/app/workspace/apps/habits/habits/${id}`);
      }

      case "archive": {
        await apiClient.habits.habitArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/apps/habits/habits`);
      }

      case "remove": {
        await apiClient.habits.habitRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/apps/habits/habits`);
      }

      case "create-publish": {
        await apiClient.publish.publishEntityCreate({
          owner: form.publishOwner,
        });

        return redirect(`/app/workspace/apps/habits/habits/${id}`);
      }

      case "activate-publish": {
        await apiClient.publish.publishEntityActivate({
          ref_id: form.publishEntityRefId,
        });

        return redirect(`/app/workspace/apps/habits/habits/${id}`);
      }

      case "to-draft-publish": {
        await apiClient.publish.publishEntityToDraft({
          ref_id: form.publishEntityRefId,
        });

        return redirect(`/app/workspace/apps/habits/habits/${id}`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
  } catch (error) {
    return handleActionApiError(error);
  }
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function Habit() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const [query] = useSearchParams();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const shouldShowALeaflet = useLeafNeedsToShowLeaflet();
  const streakSearch = query.toString();
  const habitRefId = loaderData.habit.ref_id;

  const inputsEnabled =
    navigation.state === "idle" &&
    !loaderData.habit.archived &&
    accessStatusAllowsWriterOrAbove(loaderData.accessStatus);

  const sortedInboxTasks = sortInboxTasksNaturally(loaderData.inboxTasks, {
    dueDateAscending: false,
  });
  const moreInfoByRefId: { [key: string]: InboxTaskParent } = {};
  for (const it of loaderData.inboxTasks) {
    moreInfoByRefId[it.ref_id] = {
      habit: loaderData.habit,
      habitStack: loaderData.allStacks.find(
        (stack) => stack.ref_id === loaderData.habit.stack_ref_id,
      ),
      owner: loaderData.owner,
      accessStatus: loaderData.accessStatus ?? undefined,
      location: loaderData.location ?? undefined,
    };
  }

  const timeEventEntries = loaderData.timeEventBlocks.map((block) => ({
    time_event_in_tz: timeEventInDayBlockToTimezone(
      block,
      topLevelInfo.user.timezone,
    ),
    entry: {
      habit: loaderData.habit,
      time_events: [block],
    },
  }));
  const sortedTimeEventEntries =
    sortInboxTaskTimeEventsNaturally(timeEventEntries);

  const cardActionFetcher = useFetcher();

  function handleCardMarkDone(it: InboxTask) {
    if (!inputsEnabled) {
      return;
    }
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.DONE,
      },
      {
        method: "post",
        action: "/app/workspace/core/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  function handleCardMarkNotDone(it: InboxTask) {
    if (!inputsEnabled) {
      return;
    }
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/app/workspace/core/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  return (
    <LeafPanel
      key={`habit-${loaderData.habit.ref_id}`}
      entityType={NamedEntityTag.HABIT}
      entityRefId={loaderData.habit.ref_id}
      fakeKey={`habit-${loaderData.habit.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.habit.archived}
      returnLocation="/app/workspace/apps/habits/habits"
      initialExpansionState={LeafPanelExpansionState.MEDIUM}
      shouldShowALeaflet={shouldShowALeaflet}
      publishable
      publishEntity={loaderData.publishEntity ?? undefined}
      accessable
      accessOwner={loaderData.owner}
      accessStatus={loaderData.accessStatus}
    >
      <NestingAwareBlock shouldHide={shouldShowALeaflet}>
        <GlobalError actionResult={actionData} />
        <HabitPropertiesEditor
          title="Properties"
          topLevelInfo={topLevelInfo}
          lifePlan={loaderData.lifePlan}
          allAspects={loaderData.allAspects ?? []}
          allChapters={loaderData.allChapters ?? []}
          allGoals={loaderData.allGoals ?? []}
          allMilestones={loaderData.allMilestones ?? []}
          allTags={loaderData.allTags}
          tags={loaderData.tags}
          allContacts={loaderData.allContacts}
          contacts={loaderData.contacts}
          location={loaderData.location}
          inputsEnabled={inputsEnabled}
          entityOwner={loaderData.owner}
          habit={loaderData.habit}
          allStacks={loaderData.allStacks}
          aspect={loaderData.aspect}
          chapter={loaderData.chapter}
          goal={loaderData.goal}
          actionData={actionData}
        />

        <SectionCard
          id="habit-streak"
          title="Streak"
          actions={
            <SectionActions
              id="habit-streak"
              topLevelInfo={topLevelInfo}
              inputsEnabled={inputsEnabled}
              actions={[
                NavSingle({
                  text: "Reset Streak",
                  link: `/app/workspace/apps/habits/habits/${habitRefId}/streak-inactive-periods/reset${streakSearch === "" ? "" : `?${streakSearch}`}`,
                }),
                NavSingle({
                  text: "Mark Range Inactive",
                  link: `/app/workspace/apps/habits/habits/${habitRefId}/streak-inactive-periods/new${streakSearch === "" ? "" : `?${streakSearch}`}`,
                }),
              ]}
            />
          }
        >
          <HabitStreakCalendar
            earliestDate={loaderData.streakMarkEarliestDate}
            latestDate={loaderData.streakMarkLatestDate}
            currentToday={topLevelInfo.today}
            habit={loaderData.habit}
            streakMarks={loaderData.streakMarks}
            inactivePeriods={loaderData.streakInactivePeriods}
            showNav
            getNavUrl={(earliestDate, latestDate) =>
              `/app/workspace/apps/habits/habits/${loaderData.habit.ref_id}?${newURLParams(
                query,
                "viewOneIncludeStreakMarksEarliestDate",
                earliestDate,
                "viewOneIncludeStreakMarksLatestDate",
                latestDate,
              )}`
            }
          />
          <StreakInactivePeriodStack
            habitRefId={habitRefId}
            periods={loaderData.streakInactivePeriods}
            search={streakSearch}
          />
        </SectionCard>

        <SectionCard
          title="Note"
          actions={
            <SectionActions
              id="habit-note"
              topLevelInfo={topLevelInfo}
              inputsEnabled={inputsEnabled}
              actions={[
                ActionSingle({
                  text: "Create Note",
                  value: "create-note",
                  highlight: false,
                  disabled: loaderData.note !== null,
                }),
              ]}
            />
          }
        >
          {loaderData.note && (
            <>
              <EntityNoteEditor
                initialNote={loaderData.note}
                inputsEnabled={inputsEnabled}
              />
            </>
          )}
        </SectionCard>

        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.SCHEDULE,
        ) && (
          <TimeEventInDayBlockStack
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            title="Time Events"
            createLocation={`/app/workspace/calendar/time-event/in-day-block/new-for-habit?habitRefId=${loaderData.habit.ref_id}`}
            entries={sortedTimeEventEntries}
          />
        )}

        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.TIME_PLANS,
        ) &&
          loaderData.timePlanActivities && (
            <SectionCard
              id="habit-time-plans"
              title="Time Plans"
              actions={
                <SectionActions
                  id="habit-time-plans-actions"
                  topLevelInfo={topLevelInfo}
                  inputsEnabled={inputsEnabled}
                  actions={[
                    NavSingle({
                      text: "Add",
                      highlight: false,
                      link: `/app/workspace/apps/time-plans/add-habit-to-plans?habitRefId=${loaderData.habit.ref_id}`,
                    }),
                  ]}
                />
              }
            >
              <TimePlanActivityList
                topLevelInfo={topLevelInfo}
                activities={loaderData.timePlanActivities.map(
                  (entry) => entry.time_plan_activity,
                )}
                timePlansByRefId={
                  new Map(
                    loaderData.timePlanActivities.map((entry) => [
                      entry.time_plan.ref_id,
                      entry.time_plan,
                    ]),
                  )
                }
                inboxTasksByRefId={new Map()}
                bigPlansByRefId={new Map()}
                todoTasksByRefId={new Map()}
                habitsByRefId={
                  new Map([[loaderData.habit.ref_id, loaderData.habit]])
                }
                choresByRefId={new Map()}
                activityDoneness={{}}
                timeEventsByRefId={new Map()}
                fullInfo={false}
                showTimePlanName={true}
              />
            </SectionCard>
          )}

        <SectionCard title="Inbox Tasks">
          {sortedInboxTasks.length > 0 && (
            <InboxTaskStack
              topLevelInfo={topLevelInfo}
              showOptions={{
                showStatus: true,
                showDueDate: true,
                showHandleMarkDone: inputsEnabled,
                showHandleMarkNotDone: inputsEnabled,
              }}
              inboxTasks={sortedInboxTasks}
              moreInfoByRefId={moreInfoByRefId}
              withPages={{
                retrieveOffsetParamName: "inboxTasksRetrieveOffset",
                totalCnt: loaderData.inboxTasksTotalCnt,
                pageSize: loaderData.inboxTasksPageSize,
              }}
              onCardMarkDone={inputsEnabled ? handleCardMarkDone : undefined}
              onCardMarkNotDone={
                inputsEnabled ? handleCardMarkNotDone : undefined
              }
            />
          )}
        </SectionCard>
      </NestingAwareBlock>
      <NestedOutlet />
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/apps/habits/habits",
  ParamsSchema,
  {
    notFound: (params) => `Could not find habit with ID ${params.id}!`,
    error: (params) =>
      `There was an error loading habit with ID ${params.id}! Please try again!`,
  },
);

function mergeCurrentStack(
  stacks: HabitStack[],
  current: HabitStack | null,
): HabitStack[] {
  if (current === null) {
    return stacks;
  }
  if (stacks.some((stack) => stack.ref_id === current.ref_id)) {
    return stacks;
  }
  return [...stacks, current];
}
