import type {
  DragStart,
  DroppableStateSnapshot,
  DropResult,
} from "@hello-pangea/dnd";
import { DragDropContext, Draggable, Droppable } from "@hello-pangea/dnd";
import {
  Box,
  Button,
  ButtonGroup,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  FormGroup,
  Stack,
  styled,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, useFetcher, useOutlet } from "@remix-run/react";

import type { InboxTask, InboxTaskFindResultEntry } from "jupiter-gen";
import {
  Eisen,
  InboxTaskSource,
  InboxTaskStatus,
  RecurringTaskPeriod,
} from "jupiter-gen";
import { memo, useContext, useState } from "react";
import { InboxTaskStatusTag } from "~/components/inbox-task-status-tag";

import Grid from "@mui/material/Unstable_Grid2";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import React from "react";
import { z } from "zod";
import { getLoggedInApiClient } from "~/api-clients";
import type { InboxTaskShowOptions } from "~/components/inbox-task-card";
import { InboxTaskCard } from "~/components/inbox-task-card";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { ActionHeader } from "~/components/infra/actions-header";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
import { NoTasksCard } from "~/components/no-tasks-card";
import { TabPanel } from "~/components/tab-panel";
import { GlobalPropertiesContext } from "~/global-properties-client";
import type { SomeErrorNoData } from "~/logic/action-result";
import { eisenIcon, eisenName } from "~/logic/domain/eisen";
import type {
  InboxTaskOptimisticState,
  InboxTaskParent,
} from "~/logic/domain/inbox-task";
import {
  canInboxTaskBeInStatus,
  filterInboxTasksForDisplay,
  isInboxTaskCoreFieldEditable,
  sortInboxTasksByEisenAndDifficulty,
  sortInboxTasksNaturally,
} from "~/logic/domain/inbox-task";
import {
  inboxTaskStatusIcon,
  inboxTaskStatusName,
} from "~/logic/domain/inbox-task-status";
import {
  ActionableTime,
  actionableTimeToDateTime,
} from "~/rendering/actionable-time";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";

enum DragTargetStatus {
  SOURCE_DRAG,
  SELECT_DRAG,
  ALLOW_DRAG,
  FORBID_DRAG,
  FREE,
}

enum View {
  SWIFTVIEW = "siwiftview",
  KANBAN_BY_EISEN = "kanban-by-eisen",
  KANBAN = "kanban",
  LIST = "list",
}

const EISENS = [
  Eisen.IMPORTANT_AND_URGENT,
  Eisen.URGENT,
  Eisen.IMPORTANT,
  Eisen.REGULAR,
];

const INBOX_TASK_STATUSES = [
  InboxTaskStatus.ACCEPTED,
  InboxTaskStatus.RECURRING,
  InboxTaskStatus.IN_PROGRESS,
  InboxTaskStatus.BLOCKED,
  InboxTaskStatus.NOT_DONE,
  InboxTaskStatus.DONE,
];

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).inboxTask.findInboxTask({
    allow_archived: false,
  });
  return json({
    entries: response.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction = ({
  actionResult,
  currentParams,
  currentUrl,
  defaultShouldRevalidate,
  formAction,
  formData,
  formEncType,
  formMethod,
  nextParams,
  nextUrl,
}) => {
  if (formAction === "/workspace/inbox-tasks/update-status-and-eisen") {
    return false;
  }

  return defaultShouldRevalidate;
};

export default function InboxTasks() {
  const topLevelInfo = useContext(TopLevelInfoContext);
  const outlet = useOutlet();
  const { entries } = useLoaderDataSafeForAnimation<typeof loader>();

  const globalProperties = useContext(GlobalPropertiesContext);

  const isBigScreen = useBigScreen();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedInboxTasks = sortInboxTasksNaturally(
    entries.map((e) => e.inbox_task)
  );
  const inboxTasksByRefId: { [key: string]: InboxTask } = {};
  for (const entry of entries) {
    inboxTasksByRefId[entry.inbox_task.ref_id.the_id] = entry.inbox_task;
  }
  const entriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of entries) {
    entriesByRefId[entry.inbox_task.ref_id.the_id] = {
      bigPlan: entry.big_plan,
      slackTask: entry.slack_task,
      emailTask: entry.email_task,
      ...entry,
    };
  }

  const [selectedView, setSelectedView] = useState(View.SWIFTVIEW);

  const kanbanBoardMoveFetcher = useFetcher<SomeErrorNoData>();
  const [optimisticUpdates, setOptimisticUpdates] = useState<{
    [key: string]: InboxTaskOptimisticState;
  }>({});
  const [draggedInboxTaskId, setDraggedInboxTaskId] = useState<
    string | undefined
  >(undefined);

  function onDragStart(start: DragStart) {
    setDraggedInboxTaskId(start.draggableId);
  }

  function onDragEnd(result: DropResult) {
    setDraggedInboxTaskId(undefined);

    if (!result.destination) {
      return null;
    }

    const destination = result.destination.droppableId.split(":");

    const eisenSchema = z
      .nativeEnum(Eisen)
      .or(z.literal("undefined").transform((_) => undefined));
    const statusSchema = z.nativeEnum(InboxTaskStatus);

    const eisen = eisenSchema.parse(destination[1]);
    const status = statusSchema.parse(destination[2]);

    const inboxTask = inboxTasksByRefId[result.draggableId];

    if (!isInboxTaskCoreFieldEditable(inboxTask.source)) {
      if (eisen && inboxTask.eisen !== eisen) {
        return null;
      }
    }

    setOptimisticUpdates((oldOptimisticUpdates) => {
      return {
        ...oldOptimisticUpdates,
        [result.draggableId]: {
          status: status,
          eisen: eisen,
        },
      };
    });

    if (isInboxTaskCoreFieldEditable(inboxTask.source)) {
      kanbanBoardMoveFetcher.submit(
        {
          id: result.draggableId,
          eisen: eisen?.toString() || "no-go",
          status: status,
        },
        {
          method: "post",
          action: "/workspace/inbox-tasks/update-status-and-eisen",
        }
      );
    } else {
      kanbanBoardMoveFetcher.submit(
        { id: result.draggableId, eisen: "no-go", status: status },
        {
          method: "post",
          action: "/workspace/inbox-tasks/update-status-and-eisen",
        }
      );
    }
  }

  function handleCardMarkDone(it: InboxTask) {
    setOptimisticUpdates((oldOptimisticUpdates) => {
      return {
        ...oldOptimisticUpdates,
        [it.ref_id.the_id]: {
          status: InboxTaskStatus.DONE,
          eisen: oldOptimisticUpdates[it.ref_id.the_id]?.eisen ?? it.eisen,
        },
      };
    });

    setTimeout(() => {
      kanbanBoardMoveFetcher.submit(
        {
          id: it.ref_id.the_id,
          status: InboxTaskStatus.DONE,
        },
        {
          method: "post",
          action: "/workspace/inbox-tasks/update-status-and-eisen",
        }
      );
    }, 0);
  }

  function handleCardMarkNotDone(it: InboxTask) {
    setOptimisticUpdates((oldOptimisticUpdates) => {
      return {
        ...oldOptimisticUpdates,
        [it.ref_id.the_id]: {
          status: InboxTaskStatus.NOT_DONE,
          eisen: oldOptimisticUpdates[it.ref_id.the_id]?.eisen ?? it.eisen,
        },
      };
    });

    setTimeout(() => {
      kanbanBoardMoveFetcher.submit(
        {
          id: it.ref_id.the_id,
          status: InboxTaskStatus.NOT_DONE,
        },
        {
          method: "post",
          action: "/workspace/inbox-tasks/update-status-and-eisen",
        }
      );
    }, 0);
  }

  const [showViewsDialog, setShowViewsDialog] = useState(false);
  const [showFilterDialog, setShowFilterDialog] = useState(false);
  const [selectedActionableTime, setSelectedActionableTime] = useState(
    ActionableTime.NOW
  );
  const [showEisenBoard, setShowEisenBoard] = useState({
    [Eisen.IMPORTANT_AND_URGENT]: true,
    [Eisen.URGENT]: true,
    [Eisen.IMPORTANT]: true,
    [Eisen.REGULAR]: true,
  });
  const [collapseInboxTaskStatusColumn, setCollapseInboxTaskStatusColumn] =
    useState({
      [InboxTaskStatus.NOT_STARTED]: true,
      [InboxTaskStatus.ACCEPTED]: false,
      [InboxTaskStatus.RECURRING]: false,
      [InboxTaskStatus.IN_PROGRESS]: false,
      [InboxTaskStatus.BLOCKED]: false,
      [InboxTaskStatus.NOT_DONE]: false,
      [InboxTaskStatus.DONE]: false,
    });

  const shouldDoAGc = figureOutIfGcIsRecommended(
    entries,
    optimisticUpdates,
    globalProperties.inboxTasksToAskForGC
  );

  return (
    <TrunkCard>
      <NestingAwarePanel showOutlet={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          <ButtonGroup>
            <Button
              variant="contained"
              to="/workspace/inbox-tasks/new"
              component={Link}
            >
              Create
            </Button>
          </ButtonGroup>

          {isBigScreen && (
            <ButtonGroup>
              <Button
                variant={
                  selectedView === View.SWIFTVIEW ? "contained" : "outlined"
                }
                onClick={() => setSelectedView(View.SWIFTVIEW)}
              >
                SwiftView
              </Button>
              <Button
                variant={
                  selectedView === View.KANBAN_BY_EISEN
                    ? "contained"
                    : "outlined"
                }
                onClick={() => setSelectedView(View.KANBAN_BY_EISEN)}
              >
                Kanban by Eisen
              </Button>
              <Button
                variant={
                  selectedView === View.KANBAN ? "contained" : "outlined"
                }
                onClick={() => setSelectedView(View.KANBAN)}
              >
                Kanban
              </Button>
              <Button
                variant={selectedView === View.LIST ? "contained" : "outlined"}
                onClick={() => setSelectedView(View.LIST)}
              >
                List
              </Button>
            </ButtonGroup>
          )}

          <ButtonGroup>
            {!isBigScreen && (
              <Button
                variant="outlined"
                onClick={() => setShowViewsDialog(true)}
              >
                Views
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={() => setShowFilterDialog(true)}
            >
              Filters
            </Button>
          </ButtonGroup>
        </ActionHeader>

        {shouldDoAGc && (
          <GCSection>
            There are quite a lot of finished inbox tasks. Consider doing a{" "}
            <Link to="/workspace/tools/gc">GC</Link> to decultter and speed
            things up.
          </GCSection>
        )}

        <>
          <GlobalError actionResult={kanbanBoardMoveFetcher.data} />
          <FieldError
            actionResult={kanbanBoardMoveFetcher.data}
            fieldName="/status"
          />
          <FieldError
            actionResult={kanbanBoardMoveFetcher.data}
            fieldName="/eisen"
          />
        </>

        <Dialog
          onClose={() => setShowViewsDialog(false)}
          open={showViewsDialog}
        >
          <DialogTitle>Views</DialogTitle>
          <DialogContent>
            <Stack spacing={1} useFlexGap>
              <ButtonGroup orientation="vertical">
                <Button
                  variant={
                    selectedView === View.SWIFTVIEW ? "contained" : "outlined"
                  }
                  onClick={() => setSelectedView(View.SWIFTVIEW)}
                >
                  SwiftView
                </Button>
                <Button
                  variant={
                    selectedView === View.KANBAN_BY_EISEN
                      ? "contained"
                      : "outlined"
                  }
                  onClick={() => setSelectedView(View.KANBAN_BY_EISEN)}
                >
                  Kanban by Eisen
                </Button>
                <Button
                  variant={
                    selectedView === View.KANBAN ? "contained" : "outlined"
                  }
                  onClick={() => setSelectedView(View.KANBAN)}
                >
                  Kanban
                </Button>
                <Button
                  variant={
                    selectedView === View.LIST ? "contained" : "outlined"
                  }
                  onClick={() => setSelectedView(View.LIST)}
                >
                  List
                </Button>
              </ButtonGroup>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowViewsDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        <Dialog
          onClose={() => setShowFilterDialog(false)}
          open={showFilterDialog}
        >
          <DialogTitle>Filters</DialogTitle>
          <DialogContent>
            <Stack spacing={1} useFlexGap>
              <Divider>
                <Typography variant="h6">Actionable From</Typography>
              </Divider>
              <ButtonGroup
                orientation={isBigScreen ? "horizontal" : "vertical"}
              >
                <Button
                  variant={
                    selectedActionableTime === ActionableTime.NOW
                      ? "contained"
                      : "outlined"
                  }
                  onClick={() => setSelectedActionableTime(ActionableTime.NOW)}
                >
                  From Now
                </Button>
                <Button
                  variant={
                    selectedActionableTime === ActionableTime.ONE_WEEK
                      ? "contained"
                      : "outlined"
                  }
                  onClick={() =>
                    setSelectedActionableTime(ActionableTime.ONE_WEEK)
                  }
                >
                  From One Week
                </Button>
                <Button
                  variant={
                    selectedActionableTime === ActionableTime.ONE_MONTH
                      ? "contained"
                      : "outlined"
                  }
                  onClick={() =>
                    setSelectedActionableTime(ActionableTime.ONE_MONTH)
                  }
                >
                  From One Month
                </Button>
              </ButtonGroup>
              {selectedView === View.KANBAN_BY_EISEN && (
                <>
                  <Divider>
                    <Typography variant="h6">Show Eisen</Typography>
                  </Divider>
                  <FormGroup>
                    {EISENS.map((eisen) => (
                      <FormControlLabel
                        key={eisen}
                        label={eisenName(eisen)}
                        control={
                          <Checkbox
                            checked={showEisenBoard[eisen]}
                            onChange={(e) =>
                              setShowEisenBoard((c) => ({
                                ...c,
                                [eisen]: e.target.checked,
                              }))
                            }
                          />
                        }
                      />
                    ))}
                  </FormGroup>
                </>
              )}
              {(selectedView === View.KANBAN_BY_EISEN ||
                selectedView === View.KANBAN) && (
                <>
                  <Divider>
                    <Typography variant="h6">Collapse Columns</Typography>
                  </Divider>
                  <FormGroup>
                    {INBOX_TASK_STATUSES.map((status) => (
                      <FormControlLabel
                        key={status}
                        label={inboxTaskStatusName(status)}
                        control={
                          <Checkbox
                            checked={collapseInboxTaskStatusColumn[status]}
                            onChange={(e) =>
                              setCollapseInboxTaskStatusColumn((c) => ({
                                ...c,
                                [status]: e.target.checked,
                              }))
                            }
                          />
                        }
                      />
                    ))}
                  </FormGroup>
                </>
              )}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowFilterDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {selectedView === View.SWIFTVIEW && (
          <SwiftView
            topLevelInfo={topLevelInfo}
            isBigScreen={isBigScreen}
            inboxTasks={sortedInboxTasks}
            optimisticUpdates={optimisticUpdates}
            moreInfoByRefId={entriesByRefId}
            actionableTime={selectedActionableTime}
            onCardMarkDone={handleCardMarkDone}
            onCardMarkNotDone={handleCardMarkNotDone}
          />
        )}

        {selectedView === View.KANBAN_BY_EISEN && (
          <>
            {isBigScreen && (
              <DragDropContext onDragStart={onDragStart} onDragEnd={onDragEnd}>
                <BigScreenKanbanByEisen
                  topLevelInfo={topLevelInfo}
                  inboxTasks={sortedInboxTasks}
                  optimisticUpdates={optimisticUpdates}
                  inboxTasksByRefId={inboxTasksByRefId}
                  moreInfoByRefId={entriesByRefId}
                  actionableTime={selectedActionableTime}
                  draggedInboxTaskId={draggedInboxTaskId}
                  showEisenBoard={showEisenBoard}
                  collapseInboxTaskStatusColumn={collapseInboxTaskStatusColumn}
                />
              </DragDropContext>
            )}

            {!isBigScreen && (
              <SmallScreenKanbanByEisen
                topLevelInfo={topLevelInfo}
                inboxTasks={sortedInboxTasks}
                optimisticUpdates={optimisticUpdates}
                moreInfoByRefId={entriesByRefId}
                actionableTime={selectedActionableTime}
                showEisenBoard={showEisenBoard}
                collapseInboxTaskStatusColumn={collapseInboxTaskStatusColumn}
                onCardMarkDone={handleCardMarkDone}
                onCardMarkNotDone={handleCardMarkNotDone}
              />
            )}
          </>
        )}

        {selectedView === View.KANBAN && (
          <>
            {isBigScreen && (
              <DragDropContext onDragStart={onDragStart} onDragEnd={onDragEnd}>
                <BigScreenKanban
                  topLevelInfo={topLevelInfo}
                  inboxTasks={sortedInboxTasks}
                  optimisticUpdates={optimisticUpdates}
                  inboxTasksByRefId={inboxTasksByRefId}
                  moreInfoByRefId={entriesByRefId}
                  actionableTime={selectedActionableTime}
                  draggedInboxTaskId={draggedInboxTaskId}
                  collapseInboxTaskStatusColumn={collapseInboxTaskStatusColumn}
                />
              </DragDropContext>
            )}

            {!isBigScreen && (
              <SmallScreenKanban
                topLevelInfo={topLevelInfo}
                inboxTasks={sortedInboxTasks}
                optimisticUpdates={optimisticUpdates}
                moreInfoByRefId={entriesByRefId}
                actionableTime={selectedActionableTime}
                collapseInboxTaskStatusColumn={collapseInboxTaskStatusColumn}
                onCardMarkDone={handleCardMarkDone}
                onCardMarkNotDone={handleCardMarkNotDone}
              />
            )}
          </>
        )}

        {selectedView === View.LIST && (
          <List
            topLevelInfo={topLevelInfo}
            inboxTasks={sortedInboxTasks}
            optimisticUpdates={optimisticUpdates}
            moreInfoByRefId={entriesByRefId}
            onCardMarkDone={handleCardMarkDone}
            onCardMarkNotDone={handleCardMarkNotDone}
          />
        )}
      </NestingAwarePanel>

      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the inbox tasks! Please try again!`
);

const GCSection = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.grey[100],
  padding: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
}));

interface SwiftViewProps {
  topLevelInfo: TopLevelInfo;
  isBigScreen: boolean;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  actionableTime: ActionableTime;
  onCardMarkDone: (inboxTask: InboxTask) => void;
  onCardMarkNotDone: (inboxTask: InboxTask) => void;
}

function SwiftView(props: SwiftViewProps) {
  const today = DateTime.now().endOf("day");
  const endOfTheWeek = today.endOf("week").endOf("day");
  const endOfTheMonth = today.endOf("month").endOf("day");
  const endOfTheQuarter = today.endOf("quarter").endOf("day");
  const endOfTheYear = today.endOf("year").endOf("day");
  const actionableTime = actionableTimeToDateTime(props.actionableTime);

  const sortedInboxTasks = sortInboxTasksByEisenAndDifficulty(props.inboxTasks);

  const inboxTasksForHabitsDueToday = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.HABIT],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: today,
      allowPeriodsIfHabit: [RecurringTaskPeriod.DAILY],
    }
  );

  const inboxTasksForHabitsDueThisWeek = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.HABIT],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheWeek,
      allowPeriodsIfHabit: [RecurringTaskPeriod.WEEKLY],
    }
  );

  const inboxTasksForHabitsDueThisMonth = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.HABIT],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheMonth,
      allowPeriodsIfHabit: [RecurringTaskPeriod.MONTHLY],
    }
  );

  const inboxTasksForHabitsDueThisQuarter = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.HABIT],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheQuarter,
      allowPeriodsIfHabit: [RecurringTaskPeriod.QUARTERLY],
    }
  );

  const inboxTasksForHabitsDueThisYear = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.HABIT],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      includeIfNoDueDate: true,
      dueDateEnd: endOfTheYear,
      allowPeriodsIfHabit: [RecurringTaskPeriod.YEARLY],
    }
  );

  const inboxTasksForChoresDueToday = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.CHORE],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: today,
      allowPeriodsIfChore: [RecurringTaskPeriod.DAILY],
    }
  );

  const inboxTasksForChoresDueThisWeek = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.CHORE],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheWeek,
      allowPeriodsIfChore: [RecurringTaskPeriod.WEEKLY],
    }
  );

  const inboxTasksForChoresDueThisMonth = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.CHORE],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheMonth,
      allowPeriodsIfChore: [RecurringTaskPeriod.MONTHLY],
    }
  );

  const inboxTasksForChoresDueThisQuarter = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.CHORE],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: endOfTheQuarter,
      allowPeriodsIfChore: [RecurringTaskPeriod.QUARTERLY],
    }
  );

  const inboxTasksForChoresDueThisYear = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [InboxTaskSource.CHORE],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      includeIfNoDueDate: true,
      dueDateEnd: endOfTheYear,
      allowPeriodsIfChore: [RecurringTaskPeriod.YEARLY],
    }
  );

  const inboxTasksForRestsDueToday = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [
        InboxTaskSource.USER,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_BIRTHDAY,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.SLACK_TASK,
        InboxTaskSource.EMAIL_TASK,
      ],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateEnd: today,
    }
  );

  const inboxTasksForRestsDueThisWeek = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [
        InboxTaskSource.USER,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_BIRTHDAY,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.SLACK_TASK,
        InboxTaskSource.EMAIL_TASK,
      ],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateStart: today,
      dueDateEnd: endOfTheWeek,
    }
  );

  const inboxTasksForRestsDueThisMonth = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [
        InboxTaskSource.USER,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_BIRTHDAY,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.SLACK_TASK,
        InboxTaskSource.EMAIL_TASK,
      ],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateStart: endOfTheWeek,
      dueDateEnd: endOfTheMonth,
    }
  );

  const inboxTasksForRestsDueThisQuarter = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [
        InboxTaskSource.USER,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_BIRTHDAY,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.SLACK_TASK,
        InboxTaskSource.EMAIL_TASK,
      ],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      dueDateStart: endOfTheMonth,
      dueDateEnd: endOfTheQuarter,
    }
  );

  const inboxTasksForRestsDueThisYear = filterInboxTasksForDisplay(
    sortedInboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowSources: [
        InboxTaskSource.USER,
        InboxTaskSource.BIG_PLAN,
        InboxTaskSource.METRIC,
        InboxTaskSource.PERSON_BIRTHDAY,
        InboxTaskSource.PERSON_CATCH_UP,
        InboxTaskSource.SLACK_TASK,
        InboxTaskSource.EMAIL_TASK,
      ],
      allowStatuses: [
        InboxTaskStatus.ACCEPTED,
        InboxTaskStatus.RECURRING,
        InboxTaskStatus.IN_PROGRESS,
        InboxTaskStatus.BLOCKED,
      ],
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      includeIfNoDueDate: true,
      dueDateStart: endOfTheQuarter,
      dueDateEnd: endOfTheYear,
    }
  );

  const habitsStack = (
    <Stack>
      <AnimatePresence>
        <InboxTaskStack
          key="habit-due-today"
          topLevelInfo={props.topLevelInfo}
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due Today"
          inboxTasks={inboxTasksForHabitsDueToday}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="habit-due-this-week"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Week"
          inboxTasks={inboxTasksForHabitsDueThisWeek}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="habit-due-this-month"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Month"
          inboxTasks={inboxTasksForHabitsDueThisMonth}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="habit-due-this-quarter"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Quarter"
          inboxTasks={inboxTasksForHabitsDueThisQuarter}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="habit-due-this-year"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Year"
          inboxTasks={inboxTasksForHabitsDueThisYear}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </AnimatePresence>
    </Stack>
  );

  const choresStack = (
    <Stack>
      <AnimatePresence>
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="chore-due-today"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due Today"
          inboxTasks={inboxTasksForChoresDueToday}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="chore-due-this-week"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Week"
          inboxTasks={inboxTasksForChoresDueThisWeek}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="chore-due-this-month"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Month"
          inboxTasks={inboxTasksForChoresDueThisMonth}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="chore-due-this-quarter"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Quarter"
          inboxTasks={inboxTasksForChoresDueThisQuarter}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="chore-due-this-year"
          showLabel
          showOptions={{
            showStatus: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Year"
          inboxTasks={inboxTasksForChoresDueThisYear}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </AnimatePresence>
    </Stack>
  );

  const restStack = (
    <Stack>
      <AnimatePresence>
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="rest-due-today"
          showLabel
          showOptions={{
            showStatus: true,
            showSource: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due Today"
          inboxTasks={inboxTasksForRestsDueToday}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="rest-due-this-week"
          showLabel
          showOptions={{
            showStatus: true,
            showSource: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Week"
          inboxTasks={inboxTasksForRestsDueThisWeek}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="rest-due-this-month"
          showLabel
          showOptions={{
            showStatus: true,
            showSource: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Month"
          inboxTasks={inboxTasksForRestsDueThisMonth}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="rest-due-this-quarter"
          showLabel
          showOptions={{
            showStatus: true,
            showSource: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Quarter"
          inboxTasks={inboxTasksForRestsDueThisQuarter}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />

        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          key="rest-due-this-year"
          showLabel
          showOptions={{
            showStatus: true,
            showSource: true,
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Due This Year"
          inboxTasks={inboxTasksForRestsDueThisYear}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </AnimatePresence>
    </Stack>
  );

  const noHabits =
    inboxTasksForHabitsDueToday.length === 0 &&
    inboxTasksForHabitsDueThisWeek.length === 0 &&
    inboxTasksForHabitsDueThisMonth.length === 0 &&
    inboxTasksForHabitsDueThisQuarter.length === 0 &&
    inboxTasksForHabitsDueThisYear.length === 0;
  const noChores =
    inboxTasksForChoresDueToday.length === 0 &&
    inboxTasksForChoresDueThisWeek.length === 0 &&
    inboxTasksForChoresDueThisMonth.length === 0 &&
    inboxTasksForChoresDueThisQuarter.length === 0 &&
    inboxTasksForChoresDueThisYear.length === 0;
  const noRests =
    inboxTasksForRestsDueToday.length === 0 &&
    inboxTasksForRestsDueThisWeek.length === 0 &&
    inboxTasksForRestsDueThisMonth.length === 0 &&
    inboxTasksForRestsDueThisQuarter.length === 0 &&
    inboxTasksForRestsDueThisYear.length === 0;
  const noNothing = noHabits && noChores && noRests;

  const noHabitsCard = (
    <NoTasksCard parent="habit" parentNewLocations="/workspace/habits/new" />
  );
  const noChoresCard = (
    <NoTasksCard parent="chore" parentNewLocations="/workspace/chores/new" />
  );
  const noRestsCard = (
    <NoTasksCard
      parent="inbox task"
      parentNewLocations="/workspace/inbox-tasks/new"
    />
  );
  const noNothingCard = noRestsCard;

  let initialSmallScreenSelectedTab = 0;
  if (!noHabits) {
    initialSmallScreenSelectedTab = 0;
  } else if (!noChores) {
    initialSmallScreenSelectedTab = 1;
  } else if (!noRests) {
    initialSmallScreenSelectedTab = 2;
  }

  const [smallScreenSelectedTab, setSmallScreenSelectedTab] = useState(
    initialSmallScreenSelectedTab
  );

  if (noNothing) {
    return <>{noNothingCard}</>;
  }

  return (
    <Grid
      container
      spacing={2}
    >
      {props.isBigScreen && !noNothing && (
        <>
          <Grid md={4}>
            <Typography variant="h5">💪 Habits</Typography>
            {!noHabits && habitsStack}
            {noHabits && noHabitsCard}
          </Grid>

          <Grid md={4}>
            <Typography variant="h5">♻️ Chores</Typography>
            {!noChores && choresStack}
            {noChores && noChoresCard}
          </Grid>

          <Grid md={4}>
            <Typography variant="h5">🌍 Rest</Typography>
            {!noRests && restStack}
            {noRests && noRestsCard}
          </Grid>
        </>
      )}

      {!props.isBigScreen && !noNothing && (
        <Grid xs={12}>
          <Tabs
            value={smallScreenSelectedTab}
            variant="fullWidth"
            onChange={(_, newValue) => setSmallScreenSelectedTab(newValue)}
          >
            <Tab icon={<p>💪</p>} iconPosition="top" label="Habits" />
            <Tab icon={<p>♻️</p>} iconPosition="top" label="Chores" />
            <Tab icon={<p>🌍</p>} iconPosition="top" label="Rest" />
          </Tabs>

          <TabPanel value={smallScreenSelectedTab} index={0}>
            {!noHabits && habitsStack}
            {noHabits && noHabitsCard}
          </TabPanel>

          <TabPanel value={smallScreenSelectedTab} index={1}>
            {!noChores && choresStack}
            {noChores && noChoresCard}
          </TabPanel>

          <TabPanel value={smallScreenSelectedTab} index={2}>
            {!noRests && restStack}
            {noRests && noRestsCard}
          </TabPanel>
        </Grid>
      )}
    </Grid>
  );
}

interface BigScreenKanbanByEisenProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  inboxTasksByRefId: { [key: string]: InboxTask };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  actionableTime: ActionableTime;
  draggedInboxTaskId?: string;
  showEisenBoard: { [key in Eisen]: boolean };
  collapseInboxTaskStatusColumn: { [key in InboxTaskStatus]: boolean };
}

function BigScreenKanbanByEisen({
  topLevelInfo,
  inboxTasks,
  optimisticUpdates,
  inboxTasksByRefId,
  moreInfoByRefId,
  actionableTime,
  draggedInboxTaskId,
  showEisenBoard,
  collapseInboxTaskStatusColumn,
}: BigScreenKanbanByEisenProps) {
  return (
    <>
      {inboxTasks.length === 0 && (
        <NoTasksCard
          parent="inbox task"
          parentNewLocations="/workspace/inbox-tasks/new"
        />
      )}
      {inboxTasks.length > 0 && (
        <>
          {EISENS.filter((e) => showEisenBoard[e]).map((e) => {
            return (
              <React.Fragment key={e}>
                <Divider>
                  <Typography variant="h6">
                    {eisenIcon(e)} {eisenName(e)}
                  </Typography>
                </Divider>
                <KanbanBoard
                  topLevelInfo={topLevelInfo}
                  inboxTasks={inboxTasks}
                  optimisticUpdates={optimisticUpdates}
                  inboxTasksByRefId={inboxTasksByRefId}
                  moreInfoByRefId={moreInfoByRefId}
                  actionableTime={actionableTime}
                  allowEisen={e}
                  draggedInboxTaskId={draggedInboxTaskId}
                  collapseInboxTaskStatusColumn={collapseInboxTaskStatusColumn}
                />
              </React.Fragment>
            );
          })}
        </>
      )}
    </>
  );
}

interface BigScreenKanbanProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  inboxTasksByRefId: { [key: string]: InboxTask };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  actionableTime: ActionableTime;
  allowEisen?: Eisen;
  draggedInboxTaskId?: string;
  collapseInboxTaskStatusColumn: { [key in InboxTaskStatus]: boolean };
}

function BigScreenKanban({
  topLevelInfo,
  inboxTasks,
  optimisticUpdates,
  inboxTasksByRefId,
  moreInfoByRefId,
  actionableTime,
  allowEisen,
  draggedInboxTaskId,
  collapseInboxTaskStatusColumn,
}: BigScreenKanbanProps) {
  return (
    <>
      {inboxTasks.length === 0 && (
        <NoTasksCard
          parent="inbox task"
          parentNewLocations="/workspace/inbox-tasks/new"
        />
      )}
      {inboxTasks.length > 0 &&
      <KanbanBoard
        topLevelInfo={topLevelInfo}
        inboxTasks={inboxTasks}
        optimisticUpdates={optimisticUpdates}
        inboxTasksByRefId={inboxTasksByRefId}
        moreInfoByRefId={moreInfoByRefId}
        actionableTime={actionableTime}
        allowEisen={allowEisen}
        draggedInboxTaskId={draggedInboxTaskId}
        collapseInboxTaskStatusColumn={collapseInboxTaskStatusColumn}
      />}
    </>
  );
}

interface KanbanBoardProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  inboxTasksByRefId: { [key: string]: InboxTask };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  actionableTime: ActionableTime;
  allowEisen?: Eisen;
  draggedInboxTaskId?: string;
  collapseInboxTaskStatusColumn: { [key in InboxTaskStatus]: boolean };
}

function KanbanBoard({
  topLevelInfo,
  inboxTasks,
  inboxTasksByRefId,
  moreInfoByRefId,
  actionableTime,
  allowEisen,
  optimisticUpdates,
  draggedInboxTaskId,
  collapseInboxTaskStatusColumn,
}: KanbanBoardProps) {
  return (
    <Grid container spacing={2}>
      <Grid xs={2}>
        <InboxTasksColumn
          topLevelInfo={topLevelInfo}
          inboxTasks={inboxTasks}
          optimisticUpdates={optimisticUpdates}
          inboxTasksByRefId={inboxTasksByRefId}
          moreInfoByRefId={moreInfoByRefId}
          actionableTime={actionableTime}
          collapsed={collapseInboxTaskStatusColumn[InboxTaskStatus.ACCEPTED]}
          allowStatus={InboxTaskStatus.ACCEPTED}
          allowEisen={allowEisen}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: allowEisen === undefined,
            showDifficulty: true,
            showDueDate: true,
          }}
          draggedInboxTaskId={draggedInboxTaskId}
        />
      </Grid>

      <Grid xs={2}>
        <InboxTasksColumn
          topLevelInfo={topLevelInfo}
          inboxTasks={inboxTasks}
          optimisticUpdates={optimisticUpdates}
          inboxTasksByRefId={inboxTasksByRefId}
          moreInfoByRefId={moreInfoByRefId}
          actionableTime={actionableTime}
          collapsed={collapseInboxTaskStatusColumn[InboxTaskStatus.RECURRING]}
          allowStatus={InboxTaskStatus.RECURRING}
          allowEisen={allowEisen}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: allowEisen === undefined,
            showDifficulty: true,
            showDueDate: true,
          }}
          draggedInboxTaskId={draggedInboxTaskId}
        />
      </Grid>

      <Grid xs={2}>
        <InboxTasksColumn
          topLevelInfo={topLevelInfo}
          inboxTasks={inboxTasks}
          optimisticUpdates={optimisticUpdates}
          inboxTasksByRefId={inboxTasksByRefId}
          moreInfoByRefId={moreInfoByRefId}
          actionableTime={actionableTime}
          collapsed={collapseInboxTaskStatusColumn[InboxTaskStatus.IN_PROGRESS]}
          allowStatus={InboxTaskStatus.IN_PROGRESS}
          allowEisen={allowEisen}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: allowEisen === undefined,
            showDifficulty: true,
            showDueDate: true,
          }}
          draggedInboxTaskId={draggedInboxTaskId}
        />
      </Grid>

      <Grid xs={2}>
        <InboxTasksColumn
          topLevelInfo={topLevelInfo}
          inboxTasks={inboxTasks}
          optimisticUpdates={optimisticUpdates}
          inboxTasksByRefId={inboxTasksByRefId}
          moreInfoByRefId={moreInfoByRefId}
          actionableTime={actionableTime}
          collapsed={collapseInboxTaskStatusColumn[InboxTaskStatus.BLOCKED]}
          allowStatus={InboxTaskStatus.BLOCKED}
          allowEisen={allowEisen}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: allowEisen === undefined,
            showDifficulty: true,
            showDueDate: true,
          }}
          draggedInboxTaskId={draggedInboxTaskId}
        />
      </Grid>

      <Grid xs={2}>
        <InboxTasksColumn
          topLevelInfo={topLevelInfo}
          inboxTasks={inboxTasks}
          optimisticUpdates={optimisticUpdates}
          inboxTasksByRefId={inboxTasksByRefId}
          moreInfoByRefId={moreInfoByRefId}
          actionableTime={actionableTime}
          collapsed={collapseInboxTaskStatusColumn[InboxTaskStatus.NOT_DONE]}
          allowStatus={InboxTaskStatus.NOT_DONE}
          allowEisen={allowEisen}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: allowEisen === undefined,
            showDifficulty: true,
            showDueDate: true,
          }}
          draggedInboxTaskId={draggedInboxTaskId}
        />
      </Grid>

      <Grid xs={2}>
        <InboxTasksColumn
          topLevelInfo={topLevelInfo}
          inboxTasks={inboxTasks}
          optimisticUpdates={optimisticUpdates}
          inboxTasksByRefId={inboxTasksByRefId}
          moreInfoByRefId={moreInfoByRefId}
          actionableTime={actionableTime}
          collapsed={collapseInboxTaskStatusColumn[InboxTaskStatus.DONE]}
          allowStatus={InboxTaskStatus.DONE}
          allowEisen={allowEisen}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: allowEisen === undefined,
            showDifficulty: true,
            showDueDate: true,
          }}
          draggedInboxTaskId={draggedInboxTaskId}
        />
      </Grid>
    </Grid>
  );
}

interface SmallScreenKanbanByEisenProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  actionableTime: ActionableTime;
  showEisenBoard: { [key in Eisen]: boolean };
  collapseInboxTaskStatusColumn: { [key in InboxTaskStatus]: boolean };
  onCardMarkDone?: (it: InboxTask) => void;
  onCardMarkNotDone?: (it: InboxTask) => void;
}

function SmallScreenKanbanByEisen(props: SmallScreenKanbanByEisenProps) {
  const actionableDate = actionableTimeToDateTime(props.actionableTime);
  const importantAndUrgentTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowEisens: [Eisen.IMPORTANT_AND_URGENT],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const urgentTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowEisens: [Eisen.URGENT],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const importantTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowEisens: [Eisen.IMPORTANT],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const regularTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowEisens: [Eisen.REGULAR],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );

  let initialSmallScreenSelectedTab = 0;
  if (importantAndUrgentTasks.length > 0) {
    initialSmallScreenSelectedTab = 0;
  } else if (urgentTasks.length > 0) {
    initialSmallScreenSelectedTab = 1;
  } else if (importantTasks.length > 0) {
    initialSmallScreenSelectedTab = 2;
  } else if (regularTasks.length > 0) {
    initialSmallScreenSelectedTab = 3;
  }

  const [smallScreenSelectedTab, setSmallScreenSelectedTab] = useState(
    initialSmallScreenSelectedTab
  );

  return (
    <>
      <Tabs
        value={smallScreenSelectedTab}
        variant="fullWidth"
        onChange={(_, newValue) => setSmallScreenSelectedTab(newValue)}
      >
        {props.showEisenBoard[Eisen.IMPORTANT_AND_URGENT] && (
          <Tab
            sx={{ minWidth: "25%" }}
            icon={eisenIcon(Eisen.IMPORTANT_AND_URGENT)}
          />
        )}
        {props.showEisenBoard[Eisen.URGENT] && (
          <Tab sx={{ minWidth: "25%" }} icon={eisenIcon(Eisen.URGENT)} />
        )}
        {props.showEisenBoard[Eisen.IMPORTANT] && (
          <Tab sx={{ minWidth: "25%" }} icon={eisenIcon(Eisen.IMPORTANT)} />
        )}
        {props.showEisenBoard[Eisen.REGULAR] && (
          <Tab sx={{ minWidth: "25%" }} icon={eisenIcon(Eisen.REGULAR)} />
        )}
      </Tabs>

      <TabPanel value={smallScreenSelectedTab} index={0}>
        <SmallScreenKanban
          topLevelInfo={props.topLevelInfo}
          inboxTasks={importantAndUrgentTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          allowEisen={Eisen.IMPORTANT_AND_URGENT}
          actionableTime={props.actionableTime}
          collapseInboxTaskStatusColumn={props.collapseInboxTaskStatusColumn}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={1}>
        <SmallScreenKanban
          topLevelInfo={props.topLevelInfo}
          inboxTasks={urgentTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          allowEisen={Eisen.URGENT}
          actionableTime={props.actionableTime}
          collapseInboxTaskStatusColumn={props.collapseInboxTaskStatusColumn}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={2}>
        <SmallScreenKanban
          topLevelInfo={props.topLevelInfo}
          inboxTasks={importantTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          allowEisen={Eisen.IMPORTANT}
          actionableTime={props.actionableTime}
          collapseInboxTaskStatusColumn={props.collapseInboxTaskStatusColumn}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={3}>
        <SmallScreenKanban
          topLevelInfo={props.topLevelInfo}
          inboxTasks={regularTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          allowEisen={Eisen.REGULAR}
          actionableTime={props.actionableTime}
          collapseInboxTaskStatusColumn={props.collapseInboxTaskStatusColumn}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>
    </>
  );
}

interface SmallScreenKanbanProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  allowEisen?: Eisen;
  actionableTime: ActionableTime;
  collapseInboxTaskStatusColumn: { [key in InboxTaskStatus]: boolean };
  onCardMarkDone?: (it: InboxTask) => void;
  onCardMarkNotDone?: (it: InboxTask) => void;
}

function SmallScreenKanban(props: SmallScreenKanbanProps) {
  const actionableDate = actionableTimeToDateTime(props.actionableTime);
  const acceptedTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [InboxTaskStatus.ACCEPTED],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const recurringTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [InboxTaskStatus.RECURRING],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const inProgressTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [InboxTaskStatus.IN_PROGRESS],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const blockedTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [InboxTaskStatus.BLOCKED],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const notDoneTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [InboxTaskStatus.NOT_DONE],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );
  const doneTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [InboxTaskStatus.DONE],
      includeIfNoActionableDate: true,
      includeIfNoDueDate: true,
      actionableDateEnd: actionableDate,
    }
  );

  let initialSmallScreenSelectedTab = 0;
  if (acceptedTasks.length > 0) {
    initialSmallScreenSelectedTab = 0;
  } else if (recurringTasks.length > 0) {
    initialSmallScreenSelectedTab = 1;
  } else if (inProgressTasks.length > 0) {
    initialSmallScreenSelectedTab = 2;
  } else if (blockedTasks.length > 0) {
    initialSmallScreenSelectedTab = 3;
  } else if (notDoneTasks.length > 0) {
    initialSmallScreenSelectedTab = 4;
  } else if (doneTasks.length > 0) {
    initialSmallScreenSelectedTab = 5;
  }

  const [smallScreenSelectedTab, setSmallScreenSelectedTab] = useState(
    initialSmallScreenSelectedTab
  );

  return (
    <>
      <Tabs
        value={smallScreenSelectedTab}
        variant="scrollable"
        onChange={(_, newValue) => setSmallScreenSelectedTab(newValue)}
      >
        {!props.collapseInboxTaskStatusColumn[InboxTaskStatus.ACCEPTED] && (
          <Tab
            icon={<p>{inboxTaskStatusIcon(InboxTaskStatus.ACCEPTED)}</p>}
            iconPosition="top"
            label={inboxTaskStatusName(InboxTaskStatus.ACCEPTED)}
          />
        )}
        {!props.collapseInboxTaskStatusColumn[InboxTaskStatus.RECURRING] && (
          <Tab
            icon={<p>{inboxTaskStatusIcon(InboxTaskStatus.RECURRING)}</p>}
            iconPosition="top"
            label={inboxTaskStatusName(InboxTaskStatus.RECURRING)}
          />
        )}
        {!props.collapseInboxTaskStatusColumn[InboxTaskStatus.IN_PROGRESS] && (
          <Tab
            icon={<p>{inboxTaskStatusIcon(InboxTaskStatus.IN_PROGRESS)}</p>}
            iconPosition="top"
            label={inboxTaskStatusName(InboxTaskStatus.IN_PROGRESS)}
          />
        )}
        {!props.collapseInboxTaskStatusColumn[InboxTaskStatus.BLOCKED] && (
          <Tab
            icon={<p>{inboxTaskStatusIcon(InboxTaskStatus.BLOCKED)}</p>}
            iconPosition="top"
            label={inboxTaskStatusName(InboxTaskStatus.BLOCKED)}
          />
        )}
        {!props.collapseInboxTaskStatusColumn[InboxTaskStatus.NOT_DONE] && (
          <Tab
            icon={<p>{inboxTaskStatusIcon(InboxTaskStatus.NOT_DONE)}</p>}
            iconPosition="top"
            label={inboxTaskStatusName(InboxTaskStatus.NOT_DONE)}
          />
        )}
        {!props.collapseInboxTaskStatusColumn[InboxTaskStatus.DONE] && (
          <Tab
            icon={<p>{inboxTaskStatusIcon(InboxTaskStatus.DONE)}</p>}
            iconPosition="top"
            label={inboxTaskStatusName(InboxTaskStatus.DONE)}
          />
        )}
      </Tabs>

      <TabPanel value={smallScreenSelectedTab} index={0}>
        {acceptedTasks.length === 0 && (
          <NoTasksCard
            parent="inbox task"
            parentNewLocations="/workspace/inbox-tasks/new"
          />
        )}
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: props.allowEisen === undefined,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showParent: true,
          }}
          inboxTasks={acceptedTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={1}>
        {recurringTasks.length === 0 && (
          <NoTasksCard
            parent="inbox task"
            parentNewLocations="/workspace/inbox-tasks/new"
          />
        )}
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: props.allowEisen === undefined,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showParent: true,
          }}
          inboxTasks={recurringTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={2}>
        {inProgressTasks.length === 0 && (
          <NoTasksCard
            parent="inbox task"
            parentNewLocations="/workspace/inbox-tasks/new"
          />
        )}
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: props.allowEisen === undefined,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showParent: true,
          }}
          inboxTasks={inProgressTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={3}>
        {blockedTasks.length === 0 && (
          <NoTasksCard
            parent="inbox task"
            parentNewLocations="/workspace/inbox-tasks/new"
          />
        )}
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: props.allowEisen === undefined,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showParent: true,
          }}
          inboxTasks={blockedTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={4}>
        {notDoneTasks.length === 0 && (
          <NoTasksCard
            parent="inbox task"
            parentNewLocations="/workspace/inbox-tasks/new"
          />
        )}
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: props.allowEisen === undefined,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showParent: true,
          }}
          inboxTasks={notDoneTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>

      <TabPanel value={smallScreenSelectedTab} index={5}>
        {doneTasks.length === 0 && (
          <NoTasksCard
            parent="inbox task"
            parentNewLocations="/workspace/inbox-tasks/new"
          />
        )}
        <InboxTaskStack
          topLevelInfo={props.topLevelInfo}
          showOptions={{
            showSource: true,
            showProject: true,
            showEisen: props.allowEisen === undefined,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showParent: true,
          }}
          inboxTasks={doneTasks}
          optimisticUpdates={props.optimisticUpdates}
          moreInfoByRefId={props.moreInfoByRefId}
          onCardMarkDone={props.onCardMarkDone}
          onCardMarkNotDone={props.onCardMarkNotDone}
        />
      </TabPanel>
    </>
  );
}

interface ListProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  onCardMarkDone?: (it: InboxTask) => void;
  onCardMarkNotDone?: (it: InboxTask) => void;
}

function List({
  topLevelInfo,
  inboxTasks,
  moreInfoByRefId,
  optimisticUpdates,
  onCardMarkDone,
  onCardMarkNotDone,
}: ListProps) {
  return (
    <>
      {inboxTasks.length === 0 && (
        <NoTasksCard
          parent="inbox task"
          parentNewLocations="/workspace/inbox-tasks/new"
        />
      )}
      <InboxTaskStack
        topLevelInfo={topLevelInfo}
        showOptions={{
          showStatus: true,
          showSource: true,
          showProject: true,
          showEisen: true,
          showDifficulty: true,
          showActionableDate: true,
          showDueDate: true,
          showParent: true,
          showHandleMarkDone: true,
          showHandleMarkNotDone: true,
        }}
        inboxTasks={inboxTasks}
        moreInfoByRefId={moreInfoByRefId}
        optimisticUpdates={optimisticUpdates}
        onCardMarkDone={onCardMarkDone}
        onCardMarkNotDone={onCardMarkNotDone}
      />
    </>
  );
}

interface InboxTasksColumnProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  inboxTasksByRefId: { [key: string]: InboxTask };
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState };
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  actionableTime: ActionableTime;
  collapsed: boolean;
  allowStatus: InboxTaskStatus;
  allowEisen?: Eisen;
  showOptions: InboxTaskShowOptions;
  draggedInboxTaskId?: string;
}

function InboxTasksColumn(props: InboxTasksColumnProps) {
  function getColumnModifier(snapshot: DroppableStateSnapshot) {
    if (snapshot.draggingFromThisWith) {
      return DragTargetStatus.SOURCE_DRAG;
    }

    if (snapshot.isDraggingOver) {
      return DragTargetStatus.SELECT_DRAG;
    }

    if (props.draggedInboxTaskId !== undefined) {
      if (allowDraggingOverStatus() && allowDraggingOverEisen()) {
        return DragTargetStatus.ALLOW_DRAG;
      } else {
        return DragTargetStatus.FORBID_DRAG;
      }
    }

    return DragTargetStatus.FREE;
  }

  function allowDraggingOverEisen() {
    if (props.draggedInboxTaskId === undefined) {
      return true;
    }

    if (props.allowEisen === undefined) {
      return true;
    }

    const inboxTask = props.inboxTasksByRefId[props.draggedInboxTaskId];

    if (isInboxTaskCoreFieldEditable(inboxTask.source)) {
      return true;
    }

    return inboxTask.eisen === props.allowEisen;
  }

  function allowDraggingOverStatus() {
    if (props.draggedInboxTaskId === undefined) {
      return true;
    }

    const inboxTask = props.inboxTasksByRefId[props.draggedInboxTaskId];

    return canInboxTaskBeInStatus(inboxTask, props.allowStatus);
  }

  const actionableTime = actionableTimeToDateTime(props.actionableTime);

  const filteredInboxTasks = filterInboxTasksForDisplay(
    props.inboxTasks,
    props.moreInfoByRefId,
    props.optimisticUpdates,
    {
      allowArchived: false,
      allowStatuses: [props.allowStatus],
      allowEisens: props.allowEisen ? [props.allowEisen] : undefined,
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTime,
      includeIfNoDueDate: true,
    }
  );

  const formattedCountStr = formatTasksCount(filteredInboxTasks.length);

  return (
    <>
      <Box sx={{ paddingBottom: "1rem" }}>
        <InboxTaskStatusTag status={props.allowStatus} />
        <Typography component="span">{formattedCountStr}</Typography>
      </Box>

      <Droppable
        type="inbox-task"
        droppableId={`inbox-tasks-column:${props.allowEisen}:${props.allowStatus}`}
        direction="vertical"
        isDropDisabled={!(allowDraggingOverStatus() && allowDraggingOverEisen())}
      >
        {(provided, snapshot) => (
          <InboxTasksColumnHighDiv
            divStatus={getColumnModifier(snapshot)}
            ref={provided.innerRef}
            {...provided.droppableProps}
          >
            {!props.collapsed && (
              <InboxTaskColumnTasks
                topLevelInfo={props.topLevelInfo}
                inboxTasks={filteredInboxTasks}
                moreInfoByRefId={props.moreInfoByRefId}
                showOptions={props.showOptions}
              />
            )}

            {provided.placeholder}
          </InboxTasksColumnHighDiv>
        )}
      </Droppable>
    </>
  );
}

interface InboxTasksColumnHighDivProps {
  divStatus: DragTargetStatus;
}

const InboxTasksColumnHighDiv = styled("div")<InboxTasksColumnHighDivProps>(
  ({ theme, divStatus }) => ({
    minHeight: "100%",
    backgroundColor:
      divStatus === DragTargetStatus.SOURCE_DRAG
        ? "rgb(191, 204, 229)"
        : divStatus === DragTargetStatus.SELECT_DRAG
        ? "#f5f5f5"
        : divStatus === DragTargetStatus.ALLOW_DRAG
        ? "rgb(234, 246, 215)"
        : divStatus === DragTargetStatus.FORBID_DRAG
        ? "rgb(243, 196, 196)"
        : theme.palette.background.paper,
  })
);

interface InboxTaskColumnTasksProps {
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  moreInfoByRefId: { [key: string]: InboxTaskParent };
  showOptions: InboxTaskShowOptions;
}

const InboxTaskColumnTasks = memo(function InboxTaskColumnTasks(
  props: InboxTaskColumnTasksProps
) {
  return (
    <Stack spacing={1} useFlexGap>
      {props.inboxTasks.map((inboxTask, index) => {
        const entry = props.moreInfoByRefId[inboxTask.ref_id.the_id];

        return (
          <Draggable
            key={inboxTask.ref_id.the_id}
            draggableId={inboxTask.ref_id.the_id}
            index={index}
          >
            {(provided, snapshpt) => (
              <div
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
              >
                <InboxTaskCard
                  topLevelInfo={props.topLevelInfo}
                  compact
                  showOptions={{
                    ...props.showOptions,
                    showProject: true,
                    showParent: true,
                    showHandleMarkDone: false,
                    showHandleMarkNotDone: false,
                  }}
                  inboxTask={inboxTask}
                  parent={entry}
                />
              </div>
            )}
          </Draggable>
        );
      })}
    </Stack>
  );
});

function formatTasksCount(tasksCnt: number) {
  return tasksCnt === 0 ? "" : tasksCnt === 1 ? "1 task" : `${tasksCnt} tasks`;
}

function figureOutIfGcIsRecommended(
  entries: Array<InboxTaskFindResultEntry>,
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState },
  inboxTasksToAskForGC: number
): boolean {
  let finishedTasksCnt = 0;

  for (const entry of entries) {
    if (entry.inbox_task.ref_id.the_id in optimisticUpdates) {
      if (
        optimisticUpdates[entry.inbox_task.ref_id.the_id].status ===
        InboxTaskStatus.DONE
      ) {
        finishedTasksCnt++;
      } else if (
        optimisticUpdates[entry.inbox_task.ref_id.the_id].status ===
        InboxTaskStatus.NOT_DONE
      ) {
        finishedTasksCnt++;
      }
    } else if (entry.inbox_task.status === InboxTaskStatus.DONE) {
      finishedTasksCnt++;
    } else if (entry.inbox_task.status === InboxTaskStatus.NOT_DONE) {
      finishedTasksCnt++;
    }
  }

  return finishedTasksCnt > inboxTasksToAskForGC;
}
