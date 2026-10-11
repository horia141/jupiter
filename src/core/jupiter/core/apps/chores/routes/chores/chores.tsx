import { z } from "zod";
import type {
  Chapter,
  Contact,
  ChoreFindResultEntry,
  ChoreStack,
  Goal,
  GoalSummary,
  InboxTask,
  Aspect,
  AspectSummary,
  Tag,
} from "@jupiter/webapi-client";
import {
  WorkspaceFeature,
  DocsHelpSubject,
  InboxTaskStatus,
  RecurringTaskPeriod,
  WidgetDimension,
} from "@jupiter/webapi-client";
import ViewListIcon from "@mui/icons-material/ViewList";
import FlareIcon from "@mui/icons-material/Flare";
import FlagIcon from "@mui/icons-material/Flag";
import ViewTimelineIcon from "@mui/icons-material/ViewTimeline";
import type {
  LoaderFunctionArgs,
  ShouldRevalidateFunction,
} from "react-router";
import { useFetcher } from "react-router";
import { Box, Card, Tab, Tabs } from "@mui/material";
import { DateTime } from "luxon";
import { Fragment, useContext, useState, type JSX } from "react";

import { CHORE } from "#/core/common/sub/inbox_tasks/parent-link-namespace";
import { ChoreInboxTasksWidget } from "#/core/apps/chores/component/inbox-tasks-widget";
import { WidgetProps } from "#/core/home/component/common";
import {
  inboxTaskFindEntryToParent,
  InboxTaskOptimisticState,
  InboxTaskParent,
  sortInboxTasksNaturally,
} from "#/core/common/sub/inbox_tasks/root";
import { isWorkspaceFeatureAvailable } from "#/core/workspaces/root";
import { sortChoresNaturally } from "#/core/apps/chores/root";
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
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "#/core/infra/component/use-nested-entities";
import { TopLevelInfoContext } from "#/core/infra/top-level-context";
import { IsKeyTag } from "#/core/common/component/is-key-tag";
import { GoalTag } from "#/core/apps/life_plan/sub/goals/components/tag";
import { ChapterTag } from "#/core/apps/life_plan/sub/chapters/components/tag";
import { sortGoalsNaturally } from "#/core/apps/life_plan/sub/goals/root";
import { useBigScreen } from "#/core/infra/component/use-big-screen";
import { periodName } from "#/core/common/recurring-task-period";
import { TagTag } from "#/core/common/sub/tags/component/tag-tag";
import { ContactTag } from "#/core/common/sub/contacts/component/contact-tag";
import { LocationTag } from "#/core/common/sub/locations/component/location-tag";
import { ChoreStackTag } from "#/core/apps/chores/component/chore-stack-tag";
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

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);

  const [
    summaryResponse,
    response,
    allTags,
    allContacts,
    choreInboxTasksResponse,
  ] = await Promise.all([
    apiClient.application.getSummaries({
      include_aspects: true,
      include_goals: true,
    }),
    apiClient.chores.choreFind({
      allow_archived: false,
      include_tags: true,
      include_life_plan: true,
      include_inbox_tasks: false,
      include_notes: false,
    }),
    apiClient.tags.tagFind({
      allow_archived: false,
    }),
    apiClient.contacts.contactFind({
      allow_archived: false,
    }),
    apiClient.inboxTasks.inboxTaskFind({
      allow_archived: false,
      filter_namespace: [CHORE],
    }),
  ]);

  return {
    chores: response.entries,
    allAspects: summaryResponse.aspects as Array<AspectSummary>,
    allGoals: summaryResponse.goals as Array<GoalSummary>,
    allTags: allTags.tags as Array<Tag>,
    allContacts: allContacts.contacts as Array<Contact>,
    choreInboxTasks: choreInboxTasksResponse.entries,
  };
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

const PANEL_ID = "chores";

const FILTERS = z.object({
  tags: z.array(z.string()).default([]),
  contacts: z.array(z.string()).default([]),
  grouping: z.nativeEnum(Grouping),
  periodBreakdown: z.nativeEnum(PeriodBreakdown),
  groupVisibility: z
    .nativeEnum(GroupVisibility)
    .default(GroupVisibility.NON_EMPTY_ONLY),
});

export default function Chores() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const entriesByRefId = new Map<string, ChoreFindResultEntry>();
  for (const entry of loaderData.chores) {
    entriesByRefId.set(entry.chore.ref_id, entry);
  }

  const lifePlanAvailable = isWorkspaceFeatureAvailable(
    topLevelInfo.workspace,
    WorkspaceFeature.LIFE_PLAN,
  );
  const [
    {
      tags: selectedTagsRefId,
      contacts: selectedContactsRefId,
      grouping: selectedGrouping,
      periodBreakdown: selectedPeriodBreakdown,
      groupVisibility: selectedGroupVisibility,
    },
    setFilters,
  ] = useSectionFilters(PANEL_ID, FILTERS, {
    grouping: lifePlanAvailable ? Grouping.BY_ASPECT_AND_GOAL : Grouping.FLAT,
    periodBreakdown: isBigScreen
      ? PeriodBreakdown.BY_PERIOD
      : PeriodBreakdown.LIST,
  });

  const [mobileTab, setMobileTab] = useState<"chores" | "inbox-tasks">(
    "chores",
  );
  const [optimisticUpdates, setOptimisticUpdates] = useState<{
    [key: string]: InboxTaskOptimisticState;
  }>({});
  const kanbanBoardMoveFetcher = useFetcher();

  const sortedChoreInboxTasks = sortInboxTasksNaturally(
    loaderData.choreInboxTasks.map((e) => e.inbox_task),
  );
  const choreEntriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of loaderData.choreInboxTasks) {
    choreEntriesByRefId[entry.inbox_task.ref_id] =
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

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });

  const widgetProps: WidgetProps = {
    rightNow,
    timezone: topLevelInfo.user.timezone,
    topLevelInfo,
    choreTasks: {
      choreInboxTasks: sortedChoreInboxTasks,
      choreEntriesByRefId,
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

  const sortedChores = sortChoresNaturally(
    (loaderData.chores as Array<ChoreFindResultEntry>).map((e) => e.chore),
  ).filter((chore) => {
    const entry = entriesByRefId.get(chore.ref_id);
    const tagsOk =
      selectedTagsRefId.length === 0 ||
      entry?.tags?.some((tag: Tag) => selectedTagsRefId.includes(tag.ref_id));
    const contactsOk =
      selectedContactsRefId.length === 0 ||
      entry?.contacts?.some((contact: Contact) =>
        selectedContactsRefId.includes(contact.ref_id),
      );
    return tagsOk && contactsOk;
  });

  // Shared chores may reference aspects from another workspace. Include
  // those for grouping/display, detached from foreign parent chains.
  const viewerAspects = loaderData.allAspects || [];
  const viewerAspectRefIds = new Set(viewerAspects.map((a) => a.ref_id));
  const foreignAspects: AspectSummary[] = [];
  const seenForeignAspectRefIds = new Set<string>();
  for (const entry of loaderData.chores as Array<ChoreFindResultEntry>) {
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

  return (
    <TrunkPanel
      key={"chores"}
      createLocation="/app/workspace/apps/chores/chores/new"
      returnLocation="/app/workspace"
      actions={
        <SectionActions
          id="chores-actions"
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
              id: "chores-stacks",
              text: "Stacks",
              link: "/app/workspace/apps/chores/stacks",
            }),
          ]}
        />
      }
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {isBigScreen ? (
          <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start" }}>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              {sortedChores.length === 0 && (
                <EntityNoNothingCard
                  title="You Have To Start Somewhere"
                  message="There are no chores to show. You can create a new chore."
                  newEntityLocations="/app/workspace/apps/chores/chores/new"
                  helpSubject={DocsHelpSubject.CHORES}
                />
              )}

              {selectedGrouping === Grouping.FLAT &&
                selectedPeriodBreakdown === PeriodBreakdown.BY_PERIOD && (
                  <ChoresByPeriodsStack
                    chores={sortedChores}
                    renderStack={(subset) => (
                      <ChoresFlatStack
                        chores={subset}
                        entriesByRefId={entriesByRefId}
                        topLevelInfo={topLevelInfo}
                        showPeriodTag={false}
                      />
                    )}
                  />
                )}

              {selectedGrouping === Grouping.FLAT &&
                selectedPeriodBreakdown !== PeriodBreakdown.BY_PERIOD && (
                  <ChoresFlatStack
                    chores={sortedChores}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                    showPeriodTag={true}
                  />
                )}

              {selectedGrouping === Grouping.BY_ASPECT && (
                <ChoresByAspectStack
                  chores={sortedChores}
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
                <ChoresByAspectAndGoalStack
                  chores={sortedChores}
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
              <ChoreInboxTasksWidget {...widgetProps} />
            </Box>
          </Box>
        ) : (
          <>
            <Tabs
              value={mobileTab}
              variant="scrollable"
              scrollButtons="auto"
              onChange={(_, v) => setMobileTab(v)}
            >
              <Tab label="Chores" value="chores" />
              <Tab label="Tasks" value="inbox-tasks" />
            </Tabs>

            {mobileTab === "chores" && (
              <>
                {sortedChores.length === 0 && (
                  <EntityNoNothingCard
                    title="You Have To Start Somewhere"
                    message="There are no chores to show. You can create a new chore."
                    newEntityLocations="/app/workspace/apps/chores/chores/new"
                    helpSubject={DocsHelpSubject.CHORES}
                  />
                )}

                {selectedGrouping === Grouping.FLAT && (
                  <ChoresFlatStack
                    chores={sortedChores}
                    entriesByRefId={entriesByRefId}
                    topLevelInfo={topLevelInfo}
                    showPeriodTag={true}
                  />
                )}

                {selectedGrouping === Grouping.BY_ASPECT && (
                  <ChoresByAspectStack
                    chores={sortedChores}
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
                  <ChoresByAspectAndGoalStack
                    chores={sortedChores}
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

            {mobileTab === "inbox-tasks" && (
              <ChoreInboxTasksWidget {...widgetProps} />
            )}
          </>
        )}
      </NestingAwareBlock>

      <NestedOutlet />
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the chores! Please try again!`,
});

interface ChoreRowProps {
  choreRefId: string;
  entriesByRefId: Map<string, ChoreFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
  showAspectTag: boolean;
  showGoalTag: boolean;
  showPeriodTag: boolean;
  showStackTag?: boolean;
}

function ChoreRow(props: ChoreRowProps) {
  const entry = props.entriesByRefId.get(props.choreRefId);
  if (!entry) {
    return null;
  }
  const chore = entry.chore;

  return (
    <EntityCard
      key={`chore-${chore.ref_id}`}
      entityId={`chore-${chore.ref_id}`}
    >
      <UserLightChip
        user={entry.owner}
        currentUserRefId={props.topLevelInfo.user.ref_id}
      />
      <EntityLink to={`/app/workspace/apps/chores/chores/${chore.ref_id}`}>
        <IsKeyTag isKey={chore.is_key} />
        <EntityNameComponent name={chore.name} />
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
        {chore.suspended && <span className="tag">Suspended</span>}
        {props.showPeriodTag && <PeriodTag period={chore.gen_params.period} />}
        {props.showStackTag !== false && entry.stack && (
          <ChoreStackTag choreStack={entry.stack} />
        )}
        {chore.gen_params.eisen && <EisenTag eisen={chore.gen_params.eisen} />}
        {chore.gen_params.difficulty && (
          <DifficultyTag difficulty={chore.gen_params.difficulty} />
        )}
        {entry.tags?.map((tag: Tag) => (
          <TagTag key={tag.ref_id} tag={tag} />
        ))}
        {entry.contacts?.map((contact: Contact) => (
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

interface ChoresFlatStackProps {
  chores: Array<ChoreFindResultEntry["chore"]>;
  entriesByRefId: Map<string, ChoreFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
  showAspectTag?: boolean;
  showGoalTag?: boolean;
  showPeriodTag?: boolean;
}

function ChoresFlatStack(props: ChoresFlatStackProps) {
  const showAspectTag = props.showAspectTag ?? true;
  const showGoalTag = props.showGoalTag ?? true;
  const showPeriodTag = props.showPeriodTag ?? true;
  const blocks = groupChoresIntoStackBlocks(props.chores, props.entriesByRefId);

  return (
    <EntityStack>
      {blocks.map((block) =>
        block.stack !== null ? (
          <ChoreStackGroup
            key={`chore-stack-group-${block.stack.ref_id}`}
            stack={block.stack}
            chores={block.chores}
            entriesByRefId={props.entriesByRefId}
            topLevelInfo={props.topLevelInfo}
            showAspectTag={showAspectTag}
            showGoalTag={showGoalTag}
            showPeriodTag={showPeriodTag}
          />
        ) : (
          <ChoreRow
            key={`chore-${block.chores[0].ref_id}`}
            choreRefId={block.chores[0].ref_id}
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

interface ChoreStackGroupProps {
  stack: ChoreStack;
  chores: Array<ChoreFindResultEntry["chore"]>;
  entriesByRefId: Map<string, ChoreFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
  showAspectTag: boolean;
  showGoalTag: boolean;
  showPeriodTag: boolean;
}

function ChoreStackGroup(props: ChoreStackGroupProps) {
  return (
    <Card
      id={`chore-stack-group-${props.stack.ref_id}`}
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
          to={`/app/workspace/apps/chores/stacks/${props.stack.ref_id}`}
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
        {props.chores.map((chore) => (
          <ChoreRow
            key={`chore-${chore.ref_id}`}
            choreRefId={chore.ref_id}
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

function groupChoresIntoStackBlocks(
  chores: Array<ChoreFindResultEntry["chore"]>,
  entriesByRefId: Map<string, ChoreFindResultEntry>,
): Array<{
  stack: ChoreStack | null;
  chores: Array<ChoreFindResultEntry["chore"]>;
}> {
  const choresByStackRefId = new Map<
    string,
    Array<ChoreFindResultEntry["chore"]>
  >();
  for (const chore of chores) {
    const stack = entriesByRefId.get(chore.ref_id)?.stack;
    if (stack === undefined || stack === null) {
      continue;
    }
    const members = choresByStackRefId.get(stack.ref_id) ?? [];
    members.push(chore);
    choresByStackRefId.set(stack.ref_id, members);
  }

  const emittedStackRefIds = new Set<string>();
  const blocks: Array<{
    stack: ChoreStack | null;
    chores: Array<ChoreFindResultEntry["chore"]>;
  }> = [];
  for (const chore of chores) {
    const stack = entriesByRefId.get(chore.ref_id)?.stack ?? null;
    if (stack === null) {
      blocks.push({ stack: null, chores: [chore] });
      continue;
    }
    if (emittedStackRefIds.has(stack.ref_id)) {
      continue;
    }
    emittedStackRefIds.add(stack.ref_id);
    blocks.push({
      stack,
      chores: choresByStackRefId.get(stack.ref_id) ?? [chore],
    });
  }
  return blocks;
}

interface ChoresByAspectStackProps {
  chores: Array<ChoreFindResultEntry["chore"]>;
  isBigScreen: boolean;
  selectedPeriodBreakdown: PeriodBreakdown;
  showEmptyGroups: boolean;
  sortedAspects: Array<AspectSummary>;
  allAspectsByRefId: Map<string, AspectSummary>;
  entriesByRefId: Map<string, ChoreFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
}

function ChoresByAspectStack(props: ChoresByAspectStackProps) {
  const showPeriodTag =
    props.selectedPeriodBreakdown !== PeriodBreakdown.BY_PERIOD;
  const shouldShowByPeriods =
    props.isBigScreen &&
    props.selectedPeriodBreakdown === PeriodBreakdown.BY_PERIOD;

  return (
    <>
      {props.sortedAspects.map((aspect) => {
        const aspectChores = props.chores.filter(
          (c) => c.aspect_ref_id === aspect.ref_id,
        );
        if (aspectChores.length === 0 && !props.showEmptyGroups) {
          return null;
        }

        const fullAspectName = computeAspectHierarchicalNameFromRoot(
          aspect,
          props.allAspectsByRefId,
        );

        return (
          <Fragment key={`aspect-${aspect.ref_id}`}>
            <StandardDivider title={fullAspectName} size="large" />

            {aspectChores.length === 0 && <EmptyChoresHint />}

            {aspectChores.length > 0 && shouldShowByPeriods && (
              <ChoresByPeriodsStack
                chores={aspectChores}
                renderStack={(subset) => (
                  <ChoresFlatStack
                    chores={subset}
                    entriesByRefId={props.entriesByRefId}
                    topLevelInfo={props.topLevelInfo}
                    showAspectTag={false}
                    showGoalTag={true}
                    showPeriodTag={false}
                  />
                )}
              />
            )}

            {aspectChores.length > 0 && !shouldShowByPeriods && (
              <ChoresFlatStack
                chores={aspectChores}
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

interface ChoresByAspectAndGoalStackProps {
  chores: Array<ChoreFindResultEntry["chore"]>;
  isBigScreen: boolean;
  selectedPeriodBreakdown: PeriodBreakdown;
  showEmptyGroups: boolean;
  sortedAspects: Array<AspectSummary>;
  allAspectsByRefId: Map<string, AspectSummary>;
  sortedGoals: Array<GoalSummary>;
  allGoalsByRefId: Map<string, GoalSummary>;
  entriesByRefId: Map<string, ChoreFindResultEntry>;
  topLevelInfo: React.ContextType<typeof TopLevelInfoContext>;
}

function ChoresByAspectAndGoalStack(props: ChoresByAspectAndGoalStackProps) {
  const showPeriodTag =
    props.selectedPeriodBreakdown !== PeriodBreakdown.BY_PERIOD;
  const shouldShowByPeriods =
    props.isBigScreen &&
    props.selectedPeriodBreakdown === PeriodBreakdown.BY_PERIOD;

  return (
    <>
      {props.sortedAspects.map((aspect) => {
        const aspectChores = props.chores.filter(
          (c) => c.aspect_ref_id === aspect.ref_id,
        );
        if (aspectChores.length === 0 && !props.showEmptyGroups) {
          return null;
        }

        const fullAspectName = computeAspectHierarchicalNameFromRoot(
          aspect,
          props.allAspectsByRefId,
        );

        if (aspectChores.length === 0) {
          return (
            <Fragment key={`aspect-${aspect.ref_id}`}>
              <StandardDivider title={fullAspectName} size="large" />
              <EmptyChoresHint />
            </Fragment>
          );
        }

        const choresByGoalRefId = new Map<string, typeof aspectChores>();
        const noGoalChores: typeof aspectChores = [];
        for (const chore of aspectChores) {
          const goalRefId = chore.goal_ref_id ?? null;
          if (!goalRefId) {
            noGoalChores.push(chore);
            continue;
          }
          const existing = choresByGoalRefId.get(goalRefId) ?? [];
          existing.push(chore);
          choresByGoalRefId.set(goalRefId, existing);
        }

        const aspectGoals = props.sortedGoals
          .filter((g) => g.aspect_ref_id === aspect.ref_id)
          .filter(
            (g) => props.showEmptyGroups || choresByGoalRefId.has(g.ref_id),
          );

        return (
          <Fragment key={`aspect-${aspect.ref_id}`}>
            <StandardDivider title={fullAspectName} size="large" />

            {aspectGoals.map((goal) => {
              const goalChores = choresByGoalRefId.get(goal.ref_id) ?? [];
              if (goalChores.length === 0 && !props.showEmptyGroups) {
                return null;
              }

              return (
                <Fragment key={`aspect-${aspect.ref_id}-goal-${goal.ref_id}`}>
                  <StandardDivider
                    title={`🎯 ${fullGoalName(goal, props.allGoalsByRefId)}`}
                    size="medium"
                  />
                  {goalChores.length === 0 && <EmptyChoresHint />}
                  {goalChores.length > 0 && shouldShowByPeriods && (
                    <ChoresByPeriodsStack
                      chores={goalChores}
                      renderStack={(subset) => (
                        <ChoresFlatStack
                          chores={subset}
                          entriesByRefId={props.entriesByRefId}
                          topLevelInfo={props.topLevelInfo}
                          showAspectTag={false}
                          showGoalTag={false}
                          showPeriodTag={false}
                        />
                      )}
                    />
                  )}
                  {goalChores.length > 0 && !shouldShowByPeriods && (
                    <ChoresFlatStack
                      chores={goalChores}
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

            {noGoalChores.length > 0 && (
              <>
                <StandardDivider title="🚫 No Goal" size="medium" />
                {shouldShowByPeriods && (
                  <ChoresByPeriodsStack
                    chores={noGoalChores}
                    renderStack={(subset) => (
                      <ChoresFlatStack
                        chores={subset}
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
                  <ChoresFlatStack
                    chores={noGoalChores}
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

function EmptyChoresHint() {
  return (
    <Box sx={{ paddingBottom: 1, opacity: 0.7, fontSize: "0.9rem" }}>
      No chores.
    </Box>
  );
}

interface ChoresByPeriodsStackProps {
  chores: Array<ChoreFindResultEntry["chore"]>;
  renderStack: (chores: Array<ChoreFindResultEntry["chore"]>) => JSX.Element;
}

function ChoresByPeriodsStack(props: ChoresByPeriodsStackProps) {
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
        const subset = props.chores.filter(
          (c) => c.gen_params.period === period,
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
