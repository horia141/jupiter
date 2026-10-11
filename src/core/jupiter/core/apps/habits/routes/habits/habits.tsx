import type {
  ADate,
  Chapter,
  Contact,
  Goal,
  GoalSummary,
  HabitFindResultEntry,
  HabitStack,
  InboxTask,
  Aspect,
  AspectSummary,
  Tag,
} from "@jupiter/webapi-client";
import {
  WidgetDimension,
  WorkspaceFeature,
  DocsHelpSubject,
  InboxTaskStatus,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import ViewListIcon from "@mui/icons-material/ViewList";
import FlareIcon from "@mui/icons-material/Flare";
import FlagIcon from "@mui/icons-material/Flag";
import ViewTimelineIcon from "@mui/icons-material/ViewTimeline";
import { Box, Card, Tab, Tabs } from "@mui/material";
import type {
  LoaderFunctionArgs,
  ShouldRevalidateFunction,
} from "react-router";
import { useFetcher } from "react-router";
import { Fragment, useContext, useState, type JSX } from "react";
import { DateTime } from "luxon";
import { z } from "zod";
import { parseQuery } from "zodix";

import { HABIT } from "#/core/common/sub/inbox_tasks/parent-link-namespace";
import { isWorkspaceFeatureAvailable } from "#/core/workspaces/root";
import { sortHabitsNaturally } from "#/core/apps/habits/root";
import { TopLevelInfoContext } from "#/core/infra/top-level-context";
import { DifficultyTag } from "#/core/common/component/difficulty-tag";
import { EisenTag } from "#/core/common/component/eisen-tag";
import { EntityNameComponent } from "#/core/common/component/entity-name";
import { EntityNoNothingCard } from "#/core/infra/component/entity-no-nothing-card";
import { EntityCard, EntityLink } from "#/core/infra/component/entity-card";
import { EntityStack } from "#/core/infra/component/entity-stack";
import { makeTrunkErrorBoundary } from "#/core/infra/component/error-boundary";
import { NestingAwareBlock } from "#/core/infra/component/layout/nesting-aware-block";
import { NestedOutlet } from "#/core/infra/component/layout/nested-outlet";
import { TrunkPanel } from "#/core/infra/component/layout/trunk-panel";
import { UserLightChip } from "#/core/users/components/user-light-chip";
import {
  FilterFewOptionsCompact,
  FilterManyOptions,
  NavSingle,
  SectionActions,
} from "#/core/infra/component/section-actions";
import { StandardDivider } from "#/core/infra/component/standard-divider";
import { PeriodTag } from "#/core/common/component/period-tag";
import { AspectTag } from "#/core/apps/life_plan/sub/aspects/component/tag";
import {
  computeAspectHierarchicalNameFromRoot,
  sortAspectsByTreeOrder,
} from "#/core/apps/life_plan/sub/aspects/root";
import { sortGoalsNaturally } from "#/core/apps/life_plan/sub/goals/root";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "#/core/infra/component/use-nested-entities";
import { IsKeyTag } from "#/core/common/component/is-key-tag";
import { HabitKeyHabitStreakWidget } from "#/core/apps/habits/component/key-habit-streak-widget";
import { HabitInboxTasksWidget } from "#/core/apps/habits/component/inbox-tasks-widget";
import { WidgetProps } from "#/core/home/component/common";
import {
  inboxTaskFindEntryToParent,
  InboxTaskOptimisticState,
  InboxTaskParent,
  sortInboxTasksNaturally,
} from "#/core/common/sub/inbox_tasks/root";
import { GoalTag } from "#/core/apps/life_plan/sub/goals/components/tag";
import { ChapterTag } from "#/core/apps/life_plan/sub/chapters/components/tag";
import { useBigScreen } from "#/core/infra/component/use-big-screen";
import { periodName } from "#/core/common/recurring-task-period";
import { TagTag } from "#/core/common/sub/tags/component/tag-tag";
import { ContactTag } from "#/core/common/sub/contacts/component/contact-tag";
import { LocationTag } from "#/core/common/sub/locations/component/location-tag";
import { HabitStackTag } from "#/core/apps/habits/component/habit-stack-tag";
import { useLoaderDataSafeForAnimation } from "#/core/infra/component/use-loader-data-for-animation";
import { basicShouldRevalidate } from "#/core/infra/should-revalidate";
import { getLoggedInApiClient } from "#/core/infra/api-clients.server";
import { useSectionFilters } from "#/core/infra/component/use-section-filter";

export const handle = {
  displayType: DisplayType.TRUNK,
};

enum Grouping {
  FLAT = "flat",
  BY_ASPECT = "by-aspect",
  BY_ASPECT_AND_GOAL = "by-aspect-and-goal",
}

enum PeriodBreakdown {
  LIST = "list",
  BY_PERIOD = "by-period",
}

enum GroupVisibility {
  NON_EMPTY_ONLY = "non-empty-only",
  SHOW_ALL = "show-all",
}

const QuerySchema = z.object({
  includeStreakMarksEarliestDate: z.string().optional(),
  includeStreakMarksLatestDate: z.string().optional(),
});

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);

  let earliestDate = query.includeStreakMarksEarliestDate;
  let latestDate = query.includeStreakMarksLatestDate;
  if (earliestDate === undefined) {
    earliestDate = DateTime.now().minus({ days: 365 }).toISODate();
    latestDate = DateTime.now().toISODate();
  }

  const [
    summaryResponse,
    response,
    habitInboxTasksResponse,
    allTags,
    allContacts,
    keyHabitStreaksResponse,
  ] = await Promise.all([
    apiClient.application.getSummaries({
      include_aspects: true,
      include_goals: true,
    }),
    apiClient.habits.habitFind({
      allow_archived: false,
      include_tags: true,
      include_notes: false,
      include_life_plan: true,
      include_inbox_tasks: false,
    }),
    apiClient.inboxTasks.inboxTaskFind({
      allow_archived: false,
      filter_just_workable: true,
      filter_namespace: [HABIT],
    }),
    apiClient.tags.tagFind({
      allow_archived: false,
    }),
    apiClient.contacts.contactFind({
      allow_archived: false,
    }),
    apiClient.habits.habitFindStreaks({
      filter_only_key: true,
      include_streak_marks_earliest_date: earliestDate,
      include_streak_marks_latest_date: latestDate,
    }),
  ]);

  return {
    habits: response.entries,
    allAspects: summaryResponse.aspects as Array<AspectSummary>,
    allGoals: summaryResponse.goals as Array<GoalSummary>,
    allTags: allTags.tags,
    allContacts: allContacts.contacts as Array<Contact>,
    keyHabitStreaks: keyHabitStreaksResponse.entries.map((h) => ({
      habitRefId: h.habit.ref_id,
      streakMarkEarliestDate: keyHabitStreaksResponse.streak_mark_earliest_date,
      streakMarkLatestDate: keyHabitStreaksResponse.streak_mark_latest_date,
      streakMarks: h.streak_marks,
      inactivePeriods: h.streak_inactive_periods,
    })),
    habitInboxTasks: habitInboxTasksResponse.entries,
  };
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

const PANEL_ID = "habits";

const FILTERS = z.object({
  grouping: z.nativeEnum(Grouping),
  periodBreakdown: z.nativeEnum(PeriodBreakdown),
  groupVisibility: z
    .nativeEnum(GroupVisibility)
    .default(GroupVisibility.NON_EMPTY_ONLY),
  tags: z.array(z.string()).default([]),
  contacts: z.array(z.string()).default([]),
});

export default function Habits() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const [mobileTab, setMobileTab] = useState<"streaks" | "habits" | "tasks">(
    "streaks",
  );
  const [optimisticUpdates, setOptimisticUpdates] = useState<{
    [key: string]: InboxTaskOptimisticState;
  }>({});
  const kanbanBoardMoveFetcher = useFetcher();

  const sortedHabitInboxTasks = sortInboxTasksNaturally(
    loaderData.habitInboxTasks.map((e) => e.inbox_task),
  );
  const habitEntriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of loaderData.habitInboxTasks) {
    habitEntriesByRefId[entry.inbox_task.ref_id] =
      inboxTaskFindEntryToParent(entry);
  }

  function handleCardMarkDone(it: InboxTask) {
    setOptimisticUpdates((old) => ({
      ...old,
      [it.ref_id]: {
        status: InboxTaskStatus.DONE,
        eisen: old[it.ref_id]?.eisen ?? it.eisen,
      },
    }));
    setTimeout(() => {
      kanbanBoardMoveFetcher.submit(
        { id: it.ref_id, status: InboxTaskStatus.DONE },
        {
          method: "post",
          action: "/app/workspace/core/inbox-tasks/update-status-and-eisen",
        },
      );
    }, 0);
  }

  function handleCardMarkNotDone(it: InboxTask) {
    setOptimisticUpdates((old) => ({
      ...old,
      [it.ref_id]: {
        status: InboxTaskStatus.NOT_DONE,
        eisen: old[it.ref_id]?.eisen ?? it.eisen,
      },
    }));
    setTimeout(() => {
      kanbanBoardMoveFetcher.submit(
        { id: it.ref_id, status: InboxTaskStatus.NOT_DONE },
        {
          method: "post",
          action: "/app/workspace/core/inbox-tasks/update-status-and-eisen",
        },
      );
    }, 0);
  }

  const lifePlanAvailable = isWorkspaceFeatureAvailable(
    topLevelInfo.workspace,
    WorkspaceFeature.LIFE_PLAN,
  );

  const [
    {
      grouping: selectedGrouping,
      periodBreakdown: selectedPeriodBreakdown,
      groupVisibility: selectedGroupVisibility,
      tags: selectedTagsRefId,
      contacts: selectedContactsRefId,
    },
    setFilters,
  ] = useSectionFilters(PANEL_ID, FILTERS, {
    grouping: lifePlanAvailable ? Grouping.BY_ASPECT_AND_GOAL : Grouping.FLAT,
    periodBreakdown: isBigScreen
      ? PeriodBreakdown.BY_PERIOD
      : PeriodBreakdown.LIST,
  });

  const tagsByRefId: { [tag: string]: Tag } = {};
  for (const tag of loaderData.allTags) {
    tagsByRefId[tag.ref_id] = tag;
  }

  const entriesByRefId = new Map<string, HabitFindResultEntry>();
  for (const entry of loaderData.habits) {
    entriesByRefId.set(entry.habit.ref_id, entry);
  }

  const sortedHabits = sortHabitsNaturally(
    loaderData.habits.map((e) => e.habit),
  ).filter((habit) => {
    const tagsOk =
      selectedTagsRefId.length === 0 ||
      entriesByRefId
        .get(habit.ref_id)
        ?.tags?.some((tag) => selectedTagsRefId.includes(tag.ref_id));
    const contactsOk =
      selectedContactsRefId.length === 0 ||
      entriesByRefId
        .get(habit.ref_id)
        ?.contacts?.some((contact) =>
          selectedContactsRefId.includes(contact.ref_id),
        );
    return tagsOk && contactsOk;
  });

  // Shared habits may reference aspects from another workspace. Include
  // those for grouping/display, detached from foreign parent chains.
  const viewerAspects = loaderData.allAspects || [];
  const viewerAspectRefIds = new Set(viewerAspects.map((a) => a.ref_id));
  const foreignAspects: AspectSummary[] = [];
  const seenForeignAspectRefIds = new Set<string>();
  for (const entry of loaderData.habits as Array<HabitFindResultEntry>) {
    const aspect = entry.aspect;
    if (
      aspect === undefined ||
      aspect === null ||
      viewerAspectRefIds.has(aspect.ref_id) ||
      seenForeignAspectRefIds.has(aspect.ref_id)
    ) {
      continue;
    }
    seenForeignAspectRefIds.add(aspect.ref_id);
    foreignAspects.push({
      ref_id: aspect.ref_id,
      parent_aspect_ref_id: null,
      name: aspect.name,
      order_of_child_aspects: [],
    });
  }
  const aspectsForGrouping = [...viewerAspects, ...foreignAspects];
  const sortedAspects = sortAspectsByTreeOrder(aspectsForGrouping);
  const allAspectsByRefId = new Map(
    aspectsForGrouping.map((p) => [p.ref_id, p]),
  );

  const sortedGoals = sortGoalsNaturally(loaderData.allGoals || []);
  const allGoalsByRefId = new Map(
    loaderData.allGoals?.map((g) => [g.ref_id, g]),
  );

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });

  const streakWidgetProps: WidgetProps = {
    rightNow,
    timezone: topLevelInfo.user.timezone,
    topLevelInfo,
    habitStreak: {
      earliestDate:
        loaderData.keyHabitStreaks[0]?.streakMarkEarliestDate ??
        topLevelInfo.today,
      latestDate:
        loaderData.keyHabitStreaks[0]?.streakMarkLatestDate ??
        topLevelInfo.today,
      currentToday: topLevelInfo.today,
      entries: loaderData.keyHabitStreaks.map((h) => ({
        habit: entriesByRefId.get(h.habitRefId)!.habit,
        streakMarks: h.streakMarks,
        streakInactivePeriods: h.inactivePeriods,
      })),
      label: "Latest Streak",
      showNav: true,
      getNavUrl: (earliestDate: ADate, latestDate: ADate) => {
        return `/app/workspace/apps/habits/habits?includeStreakMarksEarliestDate=${earliestDate}&includeStreakMarksLatestDate=${latestDate}`;
      },
    },
    geometry: {
      row: 0,
      col: 0,
      dimension: WidgetDimension.DIM_3X1,
    },
  };

  const tasksWidgetProps: WidgetProps = {
    rightNow,
    timezone: topLevelInfo.user.timezone,
    topLevelInfo,
    habitTasks: {
      habits: loaderData.habits.map((e) => e.habit),
      habitInboxTasks: sortedHabitInboxTasks,
      habitEntriesByRefId,
      optimisticUpdates,
      onCardMarkDone: handleCardMarkDone,
      onCardMarkNotDone: handleCardMarkNotDone,
    },
    geometry: {
      row: 0,
      col: 0,
      dimension: WidgetDimension.DIM_1X3,
    },
  };

  return (
    <TrunkPanel
      key={"habits"}
      createLocation="/app/workspace/apps/habits/habits/new"
      returnLocation="/app/workspace"
      actions={
        <SectionActions
          id="habits-actions"
          topLevelInfo={topLevelInfo}
          inputsEnabled={true}
          actions={[
            FilterFewOptionsCompact(
              "Grouping",
              selectedGrouping,
              [
                {
                  value: Grouping.BY_ASPECT_AND_GOAL,
                  text: "By Aspect & Goal",
                  icon: <FlagIcon />,
                  gatedOn: WorkspaceFeature.LIFE_PLAN,
                },
                {
                  value: Grouping.BY_ASPECT,
                  text: "By Aspect",
                  icon: <FlareIcon />,
                  gatedOn: WorkspaceFeature.LIFE_PLAN,
                },
                { value: Grouping.FLAT, text: "Flat", icon: <ViewListIcon /> },
              ],
              (selected) => setFilters({ grouping: selected }),
            ),
            ...(isBigScreen
              ? [
                  FilterFewOptionsCompact(
                    "Periods",
                    selectedPeriodBreakdown,
                    [
                      {
                        value: PeriodBreakdown.BY_PERIOD,
                        text: "By Period",
                        icon: <ViewTimelineIcon />,
                      },
                      {
                        value: PeriodBreakdown.LIST,
                        text: "List",
                        icon: <ViewListIcon />,
                      },
                    ],
                    (selected) => setFilters({ periodBreakdown: selected }),
                  ),
                ]
              : []),
            ...(lifePlanAvailable && selectedGrouping !== Grouping.FLAT
              ? [
                  FilterFewOptionsCompact(
                    "Groups",
                    selectedGroupVisibility,
                    [
                      {
                        value: GroupVisibility.NON_EMPTY_ONLY,
                        text: "Only non-empty",
                        icon: <ViewListIcon />,
                      },
                      {
                        value: GroupVisibility.SHOW_ALL,
                        text: "Show all",
                        icon: <ViewListIcon />,
                        gatedOn: WorkspaceFeature.LIFE_PLAN,
                      },
                    ],
                    (selected) => setFilters({ groupVisibility: selected }),
                  ),
                ]
              : []),
            FilterManyOptions(
              "Tags",
              loaderData.allTags.map((tag) => ({
                value: tag.ref_id,
                text: tag.name,
              })),
              selectedTagsRefId,
              (tags) => setFilters({ tags }),
            ),
            FilterManyOptions(
              "Contacts",
              loaderData.allContacts.map((contact) => ({
                value: contact.ref_id,
                text: contact.name,
              })),
              selectedContactsRefId,
              (contacts) => setFilters({ contacts }),
            ),
            NavSingle({
              id: "habits-stacks",
              text: "Stacks",
              link: "/app/workspace/apps/habits/stacks",
            }),
          ]}
        />
      }
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {isBigScreen ? (
          <>
            {loaderData.habits.length === 0 && (
              <EntityNoNothingCard
                title="You Have To Start Somewhere"
                message="There are no habits to show. You can create a new habit."
                newEntityLocations="/app/workspace/apps/habits/habits/new"
                helpSubject={DocsHelpSubject.HABITS}
              />
            )}

            {loaderData.keyHabitStreaks.length > 0 && (
              <HabitKeyHabitStreakWidget {...streakWidgetProps} />
            )}

            <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start" }}>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                {selectedGrouping === Grouping.FLAT &&
                  selectedPeriodBreakdown === PeriodBreakdown.BY_PERIOD && (
                    <HabitsByPeriodsStack
                      habits={sortedHabits}
                      renderStack={(subset) => (
                        <HabitsFlatStack
                          habits={subset}
                          entriesByRefId={entriesByRefId}
                          topLevelInfo={topLevelInfo}
                          showPeriodTag={false}
                        />
                      )}
                    />
                  )}

                {selectedGrouping === Grouping.FLAT &&
                  selectedPeriodBreakdown !== PeriodBreakdown.BY_PERIOD && (
                    <HabitsFlatStack
                      habits={sortedHabits}
                      entriesByRefId={entriesByRefId}
                      topLevelInfo={topLevelInfo}
                      showPeriodTag={true}
                    />
                  )}

                {selectedGrouping === Grouping.BY_ASPECT && (
                  <HabitsByAspectStack
                    habits={sortedHabits}
                    isBigScreen={isBigScreen}
                    selectedPeriodBreakdown={selectedPeriodBreakdown}
                    showEmptyGroups={
                      selectedGroupVisibility === GroupVisibility.SHOW_ALL
                    }
                    sortedAspects={sortedAspects}
                    allAspectsByRefId={allAspectsByRefId}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                  />
                )}

                {selectedGrouping === Grouping.BY_ASPECT_AND_GOAL && (
                  <HabitsByAspectAndGoalStack
                    habits={sortedHabits}
                    isBigScreen={isBigScreen}
                    selectedPeriodBreakdown={selectedPeriodBreakdown}
                    showEmptyGroups={
                      selectedGroupVisibility === GroupVisibility.SHOW_ALL
                    }
                    sortedAspects={sortedAspects}
                    allAspectsByRefId={allAspectsByRefId}
                    sortedGoals={sortedGoals}
                    allGoalsByRefId={allGoalsByRefId}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                  />
                )}
              </Box>

              <Box
                sx={{
                  width: "320px",
                  flexShrink: 0,
                  position: "sticky",
                  top: "1rem",
                  maxHeight: "calc(100vh - 8rem)",
                  overflowY: "auto",
                  border: (theme) => `2px dotted ${theme.palette.primary.main}`,
                  borderRadius: "4px",
                  padding: "0.4rem",
                }}
              >
                <HabitInboxTasksWidget {...tasksWidgetProps} />
              </Box>
            </Box>
          </>
        ) : (
          <>
            <Tabs
              value={mobileTab}
              variant="scrollable"
              scrollButtons="auto"
              onChange={(_, v) => setMobileTab(v)}
            >
              <Tab label="Streaks" value="streaks" />
              <Tab label="Habits" value="habits" />
              <Tab label="Tasks" value="tasks" />
            </Tabs>

            {mobileTab === "streaks" && (
              <>
                {loaderData.habits.length === 0 && (
                  <EntityNoNothingCard
                    title="You Have To Start Somewhere"
                    message="There are no habits to show. You can create a new habit."
                    newEntityLocations="/app/workspace/apps/habits/habits/new"
                    helpSubject={DocsHelpSubject.HABITS}
                  />
                )}
                {loaderData.keyHabitStreaks.length > 0 && (
                  <HabitKeyHabitStreakWidget {...streakWidgetProps} />
                )}
              </>
            )}

            {mobileTab === "habits" && (
              <>
                {sortedHabits.length === 0 && (
                  <EntityNoNothingCard
                    title="You Have To Start Somewhere"
                    message="There are no habits to show. You can create a new habit."
                    newEntityLocations="/app/workspace/apps/habits/habits/new"
                    helpSubject={DocsHelpSubject.HABITS}
                  />
                )}

                {selectedGrouping === Grouping.FLAT && (
                  <HabitsFlatStack
                    habits={sortedHabits}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                    showPeriodTag={true}
                  />
                )}

                {selectedGrouping === Grouping.BY_ASPECT && (
                  <HabitsByAspectStack
                    habits={sortedHabits}
                    isBigScreen={isBigScreen}
                    selectedPeriodBreakdown={selectedPeriodBreakdown}
                    showEmptyGroups={
                      selectedGroupVisibility === GroupVisibility.SHOW_ALL
                    }
                    sortedAspects={sortedAspects}
                    allAspectsByRefId={allAspectsByRefId}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                  />
                )}

                {selectedGrouping === Grouping.BY_ASPECT_AND_GOAL && (
                  <HabitsByAspectAndGoalStack
                    habits={sortedHabits}
                    isBigScreen={isBigScreen}
                    selectedPeriodBreakdown={selectedPeriodBreakdown}
                    showEmptyGroups={
                      selectedGroupVisibility === GroupVisibility.SHOW_ALL
                    }
                    sortedAspects={sortedAspects}
                    allAspectsByRefId={allAspectsByRefId}
                    sortedGoals={sortedGoals}
                    allGoalsByRefId={allGoalsByRefId}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                  />
                )}
              </>
            )}

            {mobileTab === "tasks" && (
              <HabitInboxTasksWidget {...tasksWidgetProps} />
            )}
          </>
        )}
      </NestingAwareBlock>

      <NestedOutlet />
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the habits! Please try again!`,
});

interface HabitRowProps {
  habitRefId: string;
  entriesByRefId: Map<string, HabitFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
  showAspectTag: boolean;
  showGoalTag: boolean;
  showPeriodTag: boolean;
  showStackTag?: boolean;
}

function HabitRow(props: HabitRowProps) {
  const entry = props.entriesByRefId.get(props.habitRefId);
  if (!entry) {
    return null;
  }
  const habit = entry.habit;

  return (
    <EntityCard
      key={`habit-${habit.ref_id}`}
      entityId={`habit-${habit.ref_id}`}
    >
      <UserLightChip
        user={entry.owner}
        currentUserRefId={props.topLevelInfo.user.ref_id}
      />
      <EntityLink to={`/app/workspace/apps/habits/habits/${habit.ref_id}`}>
        <IsKeyTag isKey={habit.is_key} />
        <EntityNameComponent name={habit.name} />
        {props.showAspectTag &&
          isWorkspaceFeatureAvailable(
            props.topLevelInfo.workspace,
            WorkspaceFeature.LIFE_PLAN,
          ) && <AspectTag aspect={entry.aspect as Aspect} />}
        {isWorkspaceFeatureAvailable(
          props.topLevelInfo.workspace,
          WorkspaceFeature.LIFE_PLAN,
        ) &&
          entry.chapter && <ChapterTag chapter={entry.chapter as Chapter} />}
        {props.showGoalTag &&
          isWorkspaceFeatureAvailable(
            props.topLevelInfo.workspace,
            WorkspaceFeature.LIFE_PLAN,
          ) &&
          entry.goal && <GoalTag goal={entry.goal as Goal} />}
        {habit.suspended && <span className="tag">Suspended</span>}
        {props.showPeriodTag && <PeriodTag period={habit.gen_params.period} />}
        {props.showStackTag !== false && entry.stack && (
          <HabitStackTag habitStack={entry.stack} />
        )}
        {habit.gen_params.eisen && <EisenTag eisen={habit.gen_params.eisen} />}
        {habit.gen_params.difficulty && (
          <DifficultyTag difficulty={habit.gen_params.difficulty} />
        )}
        {entry.tags?.map((tag) => (
          <TagTag key={tag.ref_id} tag={tag} />
        ))}
        {entry.contacts?.map((contact) => (
          <ContactTag key={contact.ref_id} contact={contact} />
        ))}
        {entry.location && <LocationTag location={entry.location} />}
      </EntityLink>
    </EntityCard>
  );
}

function fullGoalName(
  goal: GoalSummary,
  goalsByRefId: Map<string, GoalSummary>,
): string {
  const visited = new Set<string>();
  const parts: string[] = [String(goal.name)];

  let current: GoalSummary | undefined = goal;
  while (current?.parent_goal_ref_id) {
    const parentRefId = String(current.parent_goal_ref_id);
    if (visited.has(parentRefId)) {
      break;
    }
    visited.add(parentRefId);
    const parent = goalsByRefId.get(parentRefId);
    if (!parent) {
      break;
    }
    parts.unshift(String(parent.name));
    current = parent;
  }

  return parts.join(" / ");
}

interface HabitsFlatStackProps {
  habits: Array<HabitFindResultEntry["habit"]>;
  entriesByRefId: Map<string, HabitFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
  showAspectTag?: boolean;
  showGoalTag?: boolean;
  showPeriodTag?: boolean;
}

function HabitsFlatStack(props: HabitsFlatStackProps) {
  const showAspectTag = props.showAspectTag ?? true;
  const showGoalTag = props.showGoalTag ?? true;
  const showPeriodTag = props.showPeriodTag ?? true;
  const blocks = groupHabitsIntoStackBlocks(props.habits, props.entriesByRefId);

  return (
    <EntityStack>
      {blocks.map((block) =>
        block.stack !== null ? (
          <HabitStackGroup
            key={`habit-stack-group-${block.stack.ref_id}`}
            stack={block.stack}
            habits={block.habits}
            entriesByRefId={props.entriesByRefId}
            topLevelInfo={props.topLevelInfo}
            showAspectTag={showAspectTag}
            showGoalTag={showGoalTag}
            showPeriodTag={showPeriodTag}
          />
        ) : (
          <HabitRow
            key={`habit-${block.habits[0].ref_id}`}
            habitRefId={block.habits[0].ref_id}
            entriesByRefId={props.entriesByRefId}
            topLevelInfo={props.topLevelInfo}
            showAspectTag={showAspectTag}
            showGoalTag={showGoalTag}
            showPeriodTag={showPeriodTag}
          />
        ),
      )}
    </EntityStack>
  );
}

interface HabitStackGroupProps {
  stack: HabitStack;
  habits: Array<HabitFindResultEntry["habit"]>;
  entriesByRefId: Map<string, HabitFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
  showAspectTag: boolean;
  showGoalTag: boolean;
  showPeriodTag: boolean;
}

function HabitStackGroup(props: HabitStackGroupProps) {
  return (
    <Card
      id={`habit-stack-group-${props.stack.ref_id}`}
      sx={(theme) => ({
        backgroundColor:
          theme.palette.mode === "dark"
            ? theme.palette.grey[800]
            : theme.palette.grey[100],
        overflow: "hidden",
        "& .MuiCard-root": {
          backgroundColor: theme.palette.background.paper,
        },
      })}
    >
      <Box sx={{ px: 1.5, py: 0.5 }}>
        <EntityLink
          inline
          to={`/app/workspace/apps/habits/stacks/${props.stack.ref_id}`}
        >
          <EntityNameComponent compact name={props.stack.name} />
          {props.showPeriodTag && <PeriodTag period={props.stack.period} />}
        </EntityLink>
      </Box>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 0.75,
          px: 0.75,
          pb: 0.75,
        }}
      >
        {props.habits.map((habit) => (
          <HabitRow
            key={`habit-${habit.ref_id}`}
            habitRefId={habit.ref_id}
            entriesByRefId={props.entriesByRefId}
            topLevelInfo={props.topLevelInfo}
            showAspectTag={props.showAspectTag}
            showGoalTag={props.showGoalTag}
            showPeriodTag={props.showPeriodTag}
            showStackTag={false}
          />
        ))}
      </Box>
    </Card>
  );
}

function groupHabitsIntoStackBlocks(
  habits: Array<HabitFindResultEntry["habit"]>,
  entriesByRefId: Map<string, HabitFindResultEntry>,
): Array<{
  stack: HabitStack | null;
  habits: Array<HabitFindResultEntry["habit"]>;
}> {
  const habitsByStackRefId = new Map<
    string,
    Array<HabitFindResultEntry["habit"]>
  >();
  for (const habit of habits) {
    const stack = entriesByRefId.get(habit.ref_id)?.stack;
    if (stack === undefined || stack === null) {
      continue;
    }
    const members = habitsByStackRefId.get(stack.ref_id) ?? [];
    members.push(habit);
    habitsByStackRefId.set(stack.ref_id, members);
  }

  const emittedStackRefIds = new Set<string>();
  const blocks: Array<{
    stack: HabitStack | null;
    habits: Array<HabitFindResultEntry["habit"]>;
  }> = [];
  for (const habit of habits) {
    const stack = entriesByRefId.get(habit.ref_id)?.stack ?? null;
    if (stack === null) {
      blocks.push({ stack: null, habits: [habit] });
      continue;
    }
    if (emittedStackRefIds.has(stack.ref_id)) {
      continue;
    }
    emittedStackRefIds.add(stack.ref_id);
    blocks.push({
      stack,
      habits: habitsByStackRefId.get(stack.ref_id) ?? [habit],
    });
  }
  return blocks;
}

interface HabitsByAspectStackProps {
  habits: Array<HabitFindResultEntry["habit"]>;
  isBigScreen: boolean;
  selectedPeriodBreakdown: PeriodBreakdown;
  showEmptyGroups: boolean;
  sortedAspects: Array<AspectSummary>;
  allAspectsByRefId: Map<string, AspectSummary>;
  entriesByRefId: Map<string, HabitFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
}

function HabitsByAspectStack(props: HabitsByAspectStackProps) {
  const showPeriodTag =
    props.selectedPeriodBreakdown !== PeriodBreakdown.BY_PERIOD;

  return (
    <>
      {props.sortedAspects.map((aspect) => {
        const aspectHabits = props.habits.filter(
          (h) => h.aspect_ref_id === aspect.ref_id,
        );
        if (aspectHabits.length === 0 && !props.showEmptyGroups) {
          return null;
        }

        const fullAspectName = computeAspectHierarchicalNameFromRoot(
          aspect,
          props.allAspectsByRefId,
        );

        return (
          <Fragment key={`aspect-${aspect.ref_id}`}>
            <StandardDivider title={fullAspectName} size="large" />
            {aspectHabits.length === 0 && <EmptyHabitsHint />}

            {aspectHabits.length > 0 &&
              props.isBigScreen &&
              props.selectedPeriodBreakdown === PeriodBreakdown.BY_PERIOD && (
                <HabitsByPeriodsStack
                  habits={aspectHabits}
                  renderStack={(subset) => (
                    <HabitsFlatStack
                      habits={subset}
                      entriesByRefId={props.entriesByRefId}
                      topLevelInfo={props.topLevelInfo}
                      showAspectTag={false}
                      showGoalTag={true}
                      showPeriodTag={false}
                    />
                  )}
                />
              )}

            {aspectHabits.length > 0 &&
              (!props.isBigScreen ||
                props.selectedPeriodBreakdown !==
                  PeriodBreakdown.BY_PERIOD) && (
                <HabitsFlatStack
                  habits={aspectHabits}
                  entriesByRefId={props.entriesByRefId}
                  topLevelInfo={props.topLevelInfo}
                  showAspectTag={false}
                  showGoalTag={true}
                  showPeriodTag={showPeriodTag}
                />
              )}
          </Fragment>
        );
      })}
    </>
  );
}

interface HabitsByAspectAndGoalStackProps {
  habits: Array<HabitFindResultEntry["habit"]>;
  isBigScreen: boolean;
  selectedPeriodBreakdown: PeriodBreakdown;
  showEmptyGroups: boolean;
  sortedAspects: Array<AspectSummary>;
  allAspectsByRefId: Map<string, AspectSummary>;
  sortedGoals: Array<GoalSummary>;
  allGoalsByRefId: Map<string, GoalSummary>;
  entriesByRefId: Map<string, HabitFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
}

function HabitsByAspectAndGoalStack(props: HabitsByAspectAndGoalStackProps) {
  const showPeriodTag =
    props.selectedPeriodBreakdown !== PeriodBreakdown.BY_PERIOD;

  return (
    <>
      {props.sortedAspects.map((aspect) => {
        const aspectHabits = props.habits.filter(
          (h) => h.aspect_ref_id === aspect.ref_id,
        );
        if (aspectHabits.length === 0 && !props.showEmptyGroups) {
          return null;
        }

        const fullAspectName = computeAspectHierarchicalNameFromRoot(
          aspect,
          props.allAspectsByRefId,
        );

        if (aspectHabits.length === 0) {
          return (
            <Fragment key={`aspect-${aspect.ref_id}`}>
              <StandardDivider title={fullAspectName} size="large" />
              <EmptyHabitsHint />
            </Fragment>
          );
        }

        const habitsByGoalRefId = new Map<string, typeof aspectHabits>();
        const noGoalHabits: typeof aspectHabits = [];
        for (const habit of aspectHabits) {
          const goalRefId = habit.goal_ref_id ?? null;
          if (!goalRefId) {
            noGoalHabits.push(habit);
            continue;
          }
          const existing = habitsByGoalRefId.get(goalRefId) ?? [];
          existing.push(habit);
          habitsByGoalRefId.set(goalRefId, existing);
        }

        const aspectGoals = props.sortedGoals
          .filter((g) => g.aspect_ref_id === aspect.ref_id)
          .filter(
            (g) => props.showEmptyGroups || habitsByGoalRefId.has(g.ref_id),
          );

        const shouldShowByPeriods =
          props.isBigScreen &&
          props.selectedPeriodBreakdown === PeriodBreakdown.BY_PERIOD;

        return (
          <Fragment key={`aspect-${aspect.ref_id}`}>
            <StandardDivider title={fullAspectName} size="large" />

            {aspectGoals.map((goal) => {
              const goalHabits = habitsByGoalRefId.get(goal.ref_id) ?? [];
              if (goalHabits.length === 0 && !props.showEmptyGroups) {
                return null;
              }

              return (
                <Fragment key={`aspect-${aspect.ref_id}-goal-${goal.ref_id}`}>
                  <StandardDivider
                    title={`🎯 ${fullGoalName(goal, props.allGoalsByRefId)}`}
                    size="medium"
                  />
                  {goalHabits.length === 0 && <EmptyHabitsHint />}
                  {goalHabits.length > 0 && shouldShowByPeriods && (
                    <HabitsByPeriodsStack
                      habits={goalHabits}
                      renderStack={(subset) => (
                        <HabitsFlatStack
                          habits={subset}
                          entriesByRefId={props.entriesByRefId}
                          topLevelInfo={props.topLevelInfo}
                          showAspectTag={false}
                          showGoalTag={false}
                          showPeriodTag={false}
                        />
                      )}
                    />
                  )}
                  {goalHabits.length > 0 && !shouldShowByPeriods && (
                    <HabitsFlatStack
                      habits={goalHabits}
                      entriesByRefId={props.entriesByRefId}
                      topLevelInfo={props.topLevelInfo}
                      showAspectTag={false}
                      showGoalTag={false}
                      showPeriodTag={showPeriodTag}
                    />
                  )}
                </Fragment>
              );
            })}

            {noGoalHabits.length > 0 && (
              <>
                <StandardDivider title="🚫 No Goal" size="medium" />
                {shouldShowByPeriods && (
                  <HabitsByPeriodsStack
                    habits={noGoalHabits}
                    renderStack={(subset) => (
                      <HabitsFlatStack
                        habits={subset}
                        entriesByRefId={props.entriesByRefId}
                        topLevelInfo={props.topLevelInfo}
                        showAspectTag={false}
                        showGoalTag={false}
                        showPeriodTag={false}
                      />
                    )}
                  />
                )}

                {!shouldShowByPeriods && (
                  <HabitsFlatStack
                    habits={noGoalHabits}
                    entriesByRefId={props.entriesByRefId}
                    topLevelInfo={props.topLevelInfo}
                    showAspectTag={false}
                    showGoalTag={false}
                    showPeriodTag={showPeriodTag}
                  />
                )}
              </>
            )}
          </Fragment>
        );
      })}
    </>
  );
}

function EmptyHabitsHint() {
  return (
    <Box sx={{ paddingBottom: 1, opacity: 0.7, fontSize: "0.9rem" }}>
      No habits.
    </Box>
  );
}

interface HabitsByPeriodsStackProps {
  habits: Array<HabitFindResultEntry["habit"]>;
  renderStack: (habits: Array<HabitFindResultEntry["habit"]>) => JSX.Element;
}

function HabitsByPeriodsStack(props: HabitsByPeriodsStackProps) {
  const periods = [
    RecurringTaskPeriod.DAILY,
    RecurringTaskPeriod.WEEKLY,
    RecurringTaskPeriod.MONTHLY,
    RecurringTaskPeriod.QUARTERLY,
    RecurringTaskPeriod.YEARLY,
  ] as const;

  return (
    <Box
      sx={{
        display: "flex",
        gap: 2,
        alignItems: "flex-start",
        flexWrap: "nowrap",
      }}
    >
      {periods.map((period) => {
        const subset = props.habits.filter(
          (h) => h.gen_params.period === period,
        );
        return (
          <Box
            key={`period-${period}`}
            sx={{ flexBasis: "20%", flexGrow: 1, minWidth: 0 }}
          >
            <StandardDivider title={periodName(period)} size="large" />
            {props.renderStack(subset)}
          </Box>
        );
      })}
    </Box>
  );
}
