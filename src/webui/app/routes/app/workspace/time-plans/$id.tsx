import type {
  BigPlan,
  InboxTask,
  TimePlan,
  TimePlanActivity,
  TimePlanActivityDoneness,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  RecurringTaskPeriod,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import FlareIcon from "@mui/icons-material/Flare";
import ViewListIcon from "@mui/icons-material/ViewList";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Form, Outlet, useActionData, useNavigation } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { Fragment, useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { BigPlanStack } from "~/components/big-plan-stack";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import {
  ActionSingle,
  FilterFewOptionsSpread,
  FilterManyOptions,
  NavMultipleCompact,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { JournalStack } from "~/components/journal-stack";
import { PeriodSelect } from "~/components/period-select";
import { StandardDivider } from "~/components/standard-divider";
import { TimePlanActivityList } from "~/components/time-plan-activity-list";
import { TimePlanStack } from "~/components/time-plan-stack";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { sortJournalsNaturally } from "~/logic/domain/journal";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { sortTimePlansNaturally } from "~/logic/domain/time-plan";
import { filterActivityByFeasabilityWithParents } from "~/logic/domain/time-plan-activity";
import { allowUserChanges } from "~/logic/domain/time-plan-source";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

enum View {
  MERGED = "merged",
  BY_PROJECT = "by-project",
}

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("change-time-config"),
    rightNow: z.string(),
    period: z.nativeEnum(RecurringTaskPeriod),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_workspace: true,
    include_projects: true,
  });

  try {
    const workspace = summaryResponse.workspace!;

    const result = await apiClient.timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: true,
      include_targets: true,
      include_completed_nontarget: true,
      include_other_time_plans: true,
    });

    let journalResult = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.JOURNALS)) {
      journalResult = await apiClient.journals.journalLoadForDateAndPeriod({
        right_now: result.time_plan.right_now,
        period: result.time_plan.period,
        allow_archived: false,
      });
    }

    let timeEventResult = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)) {
      timeEventResult = await apiClient.calendar.calendarLoadForDateAndPeriod({
        right_now: result.time_plan.right_now,
        period: result.time_plan.period,
      });
    }

    return json({
      allProjects: summaryResponse.projects || undefined,
      timePlan: result.time_plan,
      note: result.note,
      activities: result.activities,
      targetInboxTasks: result.target_inbox_tasks as Array<InboxTask>,
      targetBigPlans: result.target_big_plans,
      activityDoneness: result.activity_doneness as Record<
        string,
        TimePlanActivityDoneness
      >,
      completedNontargetInboxTasks:
        result.completed_nontarget_inbox_tasks as Array<InboxTask>,
      completedNontargetBigPlans: result.completed_nottarget_big_plans,
      subPeriodTimePlans: result.sub_period_time_plans as Array<TimePlan>,
      higherTimePlan: result.higher_time_plan as TimePlan,
      previousTimePlan: result.previous_time_plan as TimePlan,
      journal: journalResult?.journal,
      subPeriodJournals: journalResult?.sub_period_journals || [],
      timeEventForInboxTasks:
        timeEventResult?.entries?.inbox_task_entries || [],
      timeEventForBigPlans: [],
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
      case "change-time-config": {
        await apiClient.timePlans.timePlanChangeTimeConfig({
          ref_id: id,
          right_now: {
            should_change: true,
            value: form.rightNow,
          },
          period: {
            should_change: true,
            value: form.period,
          },
        });
        return redirect(`/app/workspace/time-plans/${id}`);
      }

      case "archive": {
        await apiClient.timePlans.timePlanArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/time-plans`);
      }

      case "remove": {
        await apiClient.timePlans.timePlanRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/time-plans`);
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

    if (error instanceof ApiError && error.status === StatusCodes.CONFLICT) {
      return json(aGlobalError(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function TimePlanView() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const isBigScreen = useBigScreen();

  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const corePropertyEditable = allowUserChanges(loaderData.timePlan.source);
  const inputsEnabled =
    navigation.state === "idle" && !loaderData.timePlan.archived;

  const targetInboxTasksByRefId = new Map<string, InboxTask>(
    loaderData.targetInboxTasks.map((it) => [it.ref_id, it]),
  );
  const actitiviesByBigPlanRefId = new Map<string, TimePlanActivity>(
    loaderData.activities
      .filter((a) => a.target === TimePlanActivityTarget.BIG_PLAN)
      .map((a) => [a.target_ref_id, a]),
  );
  const targetBigPlansByRefId = new Map<string, BigPlan>(
    loaderData.targetBigPlans
      ? loaderData.targetBigPlans.map((bp) => [bp.ref_id, bp])
      : [],
  );
  const timeEventsByRefId = new Map();
  for (const e of loaderData.timeEventForInboxTasks) {
    timeEventsByRefId.set(`it:${e.inbox_task.ref_id}`, e.time_events);
  }
  // TODO(horia141): re-enable this when we have time events for big plans.
  // for (const e of loaderData.timeEventForBigPlans) {
  //   timeEventsByRefId.set(`bp:${e.big_plan.ref_id}`, e.time_events);
  // }

  const sortedSubTimePlans = sortTimePlansNaturally(
    loaderData.subPeriodTimePlans,
  );

  const [selectedView, setSelectedView] = useState(
    inferDefaultSelectedView(topLevelInfo.workspace, loaderData.timePlan),
  );
  const [selectedKinds, setSelectedKinds] = useState<TimePlanActivityKind[]>(
    [],
  );
  const [selectedFeasabilities, setSelectedFeasabilities] = useState<
    TimePlanActivityFeasability[]
  >([]);
  const [selectedDoneness, setSelectedDoneness] = useState<boolean[]>([]);

  const mustDoActivities = filterActivityByFeasabilityWithParents(
    loaderData.activities,
    actitiviesByBigPlanRefId,
    targetInboxTasksByRefId,
    targetBigPlansByRefId,
    TimePlanActivityFeasability.MUST_DO,
  );
  const niceToHaveActivities = filterActivityByFeasabilityWithParents(
    loaderData.activities,
    actitiviesByBigPlanRefId,
    targetInboxTasksByRefId,
    targetBigPlansByRefId,
    TimePlanActivityFeasability.NICE_TO_HAVE,
  );
  const stretchActivities = filterActivityByFeasabilityWithParents(
    loaderData.activities,
    actitiviesByBigPlanRefId,
    targetInboxTasksByRefId,
    targetBigPlansByRefId,
    TimePlanActivityFeasability.STRETCH,
  );
  const otherActivities = niceToHaveActivities.concat(stretchActivities);

  useEffect(() => {
    setSelectedView(
      inferDefaultSelectedView(topLevelInfo.workspace, loaderData.timePlan),
    );
    setSelectedKinds([]);
    setSelectedFeasabilities([]);
    setSelectedDoneness([]);
  }, [topLevelInfo, loaderData]);

  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p]),
  );

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  const sortedSubJournals = sortJournalsNaturally(loaderData.subPeriodJournals);

  return (
    <BranchPanel
      key={`time-plan-${loaderData.timePlan.ref_id}`}
      showArchiveAndRemoveButton={corePropertyEditable}
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.timePlan.archived}
      returnLocation="/app/workspace/time-plans"
    >
      <Form method="post">
        <NestingAwareBlock shouldHide={shouldShowALeaf}>
          <GlobalError actionResult={actionData} />
          <SectionCardNew
            title="Properties"
            actions={
              <SectionActions
                id="time-plan-properties"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  ActionSingle({
                    id: "time-plan-change-time-config",
                    text: "Change Time Config",
                    value: "change-time-config",
                    disabled: !inputsEnabled || !corePropertyEditable,
                    highlight: true,
                  }),
                ]}
              />
            }
          >
            <Stack
              direction={isBigScreen ? "row" : "column"}
              spacing={2}
              useFlexGap
            >
              <FormControl fullWidth>
                <InputLabel id="rightNow" shrink margin="dense">
                  The Date
                </InputLabel>
                <OutlinedInput
                  type="date"
                  notched
                  label="rightNow"
                  name="rightNow"
                  readOnly={!inputsEnabled || !corePropertyEditable}
                  defaultValue={loaderData.timePlan.right_now}
                />

                <FieldError actionResult={actionData} fieldName="/right_now" />
              </FormControl>

              <FormControl fullWidth>
                <PeriodSelect
                  labelId="period"
                  label="Period"
                  name="period"
                  inputsEnabled={inputsEnabled && corePropertyEditable}
                  defaultValue={loaderData.timePlan.period}
                />
                <FieldError actionResult={actionData} fieldName="/period" />
                <FieldError actionResult={actionData} fieldName="/status" />
              </FormControl>
            </Stack>
          </SectionCardNew>
          <SectionCardNew title="Notes">
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </SectionCardNew>

          <SectionCardNew
            id="time-plan-activities"
            title="Activities"
            actions={
              <SectionActions
                id="activities"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  NavMultipleCompact({
                    navs: [
                      NavSingle({
                        text: "New Inbox Task",
                        link: `/app/workspace/inbox-tasks/new?timePlanReason=for-time-plan&timePlanRefId=${loaderData.timePlan.ref_id}`,
                      }),
                      NavSingle({
                        text: "New Big Plan",
                        link: `/app/workspace/big-plans/new?timePlanReason=for-time-plan&timePlanRefId=${loaderData.timePlan.ref_id}`,
                        gatedOn: WorkspaceFeature.BIG_PLANS,
                      }),
                      NavSingle({
                        text: "From Current Inbox Tasks",
                        link: `/app/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-inbox-tasks`,
                      }),
                      NavSingle({
                        text: "From Generated Inbox Tasks",
                        link: `/app/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-generated-inbox-tasks`,
                      }),
                      NavSingle({
                        text: "From Current Big Plans",
                        link: `/app/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-big-plans`,
                        gatedOn: WorkspaceFeature.BIG_PLANS,
                      }),
                      NavSingle({
                        text: "From Time Plans",
                        link: `/app/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-time-plans/${loaderData.timePlan.ref_id}`,
                      }),
                    ],
                  }),
                  FilterFewOptionsSpread(
                    "View",
                    selectedView,
                    [
                      {
                        value: View.MERGED,
                        text: "Merged",
                        icon: <ViewListIcon />,
                      },
                      {
                        value: View.BY_PROJECT,
                        text: "By Project",
                        icon: <FlareIcon />,
                        gatedOn: WorkspaceFeature.PROJECTS,
                      },
                    ],
                    (selected) => setSelectedView(selected),
                  ),
                ]}
                extraActions={[
                  FilterManyOptions(
                    "Kind",
                    [
                      { value: TimePlanActivityKind.FINISH, text: "Finish" },
                      {
                        value: TimePlanActivityKind.MAKE_PROGRESS,
                        text: "Make Progress",
                      },
                    ],
                    setSelectedKinds,
                  ),
                  FilterManyOptions(
                    "Feasability",
                    [
                      {
                        value: TimePlanActivityFeasability.MUST_DO,
                        text: "Must Do",
                      },
                      {
                        value: TimePlanActivityFeasability.NICE_TO_HAVE,
                        text: "Nice to Have",
                      },
                      {
                        value: TimePlanActivityFeasability.STRETCH,
                        text: "Stretch",
                      },
                    ],
                    setSelectedFeasabilities,
                  ),
                  FilterManyOptions(
                    "Done",
                    [
                      { value: true, text: "Done" },
                      { value: false, text: "Not Done" },
                    ],
                    setSelectedDoneness,
                  ),
                ]}
              />
            }
          >
            {loaderData.activities.length === 0 && (
              <EntityNoNothingCard
                title="You Have To Start Somewhere"
                message="There are no activities to show. You can create a new activity."
                newEntityLocations={`/app/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-inbox-tasks`}
                helpSubject={DocsHelpSubject.TIME_PLANS}
              />
            )}

            <Stack useFlexGap gap={2}>
              {selectedView === View.MERGED && (
                <>
                  {mustDoActivities.length > 0 && (
                    <>
                      <StandardDivider title="Must Do" size="large" />

                      <TimePlanActivityList
                        topLevelInfo={topLevelInfo}
                        activities={mustDoActivities}
                        inboxTasksByRefId={targetInboxTasksByRefId}
                        timePlansByRefId={new Map()}
                        bigPlansByRefId={targetBigPlansByRefId}
                        activityDoneness={loaderData.activityDoneness}
                        fullInfo
                        filterKind={selectedKinds}
                        filterFeasability={selectedFeasabilities}
                        filterDoneness={selectedDoneness}
                        timeEventsByRefId={timeEventsByRefId}
                      />
                    </>
                  )}

                  {niceToHaveActivities.length > 0 && (
                    <>
                      <StandardDivider title="Nice To Have" size="large" />

                      <TimePlanActivityList
                        topLevelInfo={topLevelInfo}
                        activities={niceToHaveActivities}
                        inboxTasksByRefId={targetInboxTasksByRefId}
                        timePlansByRefId={new Map()}
                        bigPlansByRefId={targetBigPlansByRefId}
                        activityDoneness={loaderData.activityDoneness}
                        fullInfo
                        filterKind={selectedKinds}
                        filterFeasability={selectedFeasabilities}
                        filterDoneness={selectedDoneness}
                        timeEventsByRefId={timeEventsByRefId}
                      />
                    </>
                  )}

                  {stretchActivities.length > 0 && (
                    <>
                      <StandardDivider title="Stretch" size="large" />

                      <TimePlanActivityList
                        topLevelInfo={topLevelInfo}
                        activities={stretchActivities}
                        inboxTasksByRefId={targetInboxTasksByRefId}
                        timePlansByRefId={new Map()}
                        bigPlansByRefId={targetBigPlansByRefId}
                        activityDoneness={loaderData.activityDoneness}
                        fullInfo
                        filterKind={selectedKinds}
                        filterFeasability={selectedFeasabilities}
                        filterDoneness={selectedDoneness}
                        timeEventsByRefId={timeEventsByRefId}
                      />
                    </>
                  )}
                </>
              )}

              {selectedView === View.BY_PROJECT && (
                <>
                  {mustDoActivities.length > 0 && (
                    <>
                      <StandardDivider title="Must Do" size="large" />

                      <TimePlanActivityList
                        topLevelInfo={topLevelInfo}
                        activities={mustDoActivities}
                        inboxTasksByRefId={targetInboxTasksByRefId}
                        timePlansByRefId={new Map()}
                        bigPlansByRefId={targetBigPlansByRefId}
                        activityDoneness={loaderData.activityDoneness}
                        fullInfo
                        filterKind={selectedKinds}
                        filterFeasability={selectedFeasabilities}
                        filterDoneness={selectedDoneness}
                        timeEventsByRefId={timeEventsByRefId}
                      />
                    </>
                  )}

                  {sortedProjects.map((p) => {
                    const theActivities = otherActivities.filter((ac) => {
                      switch (ac.target) {
                        case TimePlanActivityTarget.INBOX_TASK:
                          return (
                            targetInboxTasksByRefId.get(ac.target_ref_id)
                              ?.project_ref_id === p.ref_id
                          );
                        case TimePlanActivityTarget.BIG_PLAN:
                          return (
                            targetBigPlansByRefId.get(ac.target_ref_id)
                              ?.project_ref_id === p.ref_id
                          );
                      }
                      throw new Error("Should not get here");
                    });

                    if (theActivities.length === 0) {
                      return null;
                    }

                    const fullProjectName =
                      computeProjectHierarchicalNameFromRoot(
                        p,
                        allProjectsByRefId,
                      );

                    return (
                      <Fragment key={`project-${p.ref_id}`}>
                        <StandardDivider title={fullProjectName} size="large" />

                        <TimePlanActivityList
                          topLevelInfo={topLevelInfo}
                          activities={theActivities}
                          inboxTasksByRefId={targetInboxTasksByRefId}
                          timePlansByRefId={new Map()}
                          bigPlansByRefId={targetBigPlansByRefId}
                          activityDoneness={loaderData.activityDoneness}
                          fullInfo
                          filterKind={selectedKinds}
                          filterFeasability={selectedFeasabilities}
                          filterDoneness={selectedDoneness}
                          timeEventsByRefId={timeEventsByRefId}
                        />
                      </Fragment>
                    );
                  })}
                </>
              )}
            </Stack>
          </SectionCardNew>

          {loaderData.completedNontargetInboxTasks.length > 0 && (
            <SectionCardNew
              id="time-plan-untracked-inbox-tasks"
              title="Completed & Untracked Inbox Tasks"
            >
              <InboxTaskStack
                today={today}
                topLevelInfo={topLevelInfo}
                showOptions={{
                  showStatus: true,
                  showEisen: true,
                  showDifficulty: true,
                }}
                inboxTasks={loaderData.completedNontargetInboxTasks}
              />
            </SectionCardNew>
          )}

          {loaderData.completedNontargetBigPlans &&
            loaderData.completedNontargetBigPlans.length > 0 && (
              <SectionCardNew
                id="time-plan-untracked-big-plans"
                title="Completed & Untracked Big Plans"
              >
                <BigPlanStack
                  topLevelInfo={topLevelInfo}
                  showOptions={{
                    showStatus: true,
                    showProject: true,
                    showEisen: true,
                    showDifficulty: true,
                    showActionableDate: true,
                    showDueDate: true,
                    showHandleMarkDone: false,
                    showHandleMarkNotDone: false,
                  }}
                  bigPlans={loaderData.completedNontargetBigPlans}
                />
              </SectionCardNew>
            )}

          {sortedSubTimePlans.length > 0 && (
            <SectionCardNew id="time-plan-lower" title="Lower Time Plans">
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={sortedSubTimePlans}
              />
            </SectionCardNew>
          )}

          {loaderData.higherTimePlan && (
            <SectionCardNew id="time-plan-higher" title="Higher Time Plan">
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={[loaderData.higherTimePlan]}
              />
            </SectionCardNew>
          )}

          {loaderData.previousTimePlan && (
            <SectionCardNew id="time-plan-previous" title="Previous Time Plan">
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={[loaderData.previousTimePlan]}
              />
            </SectionCardNew>
          )}

          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.JOURNALS,
          ) &&
            (loaderData.journal || sortedSubJournals.length > 0) && (
              <SectionCardNew
                id="time-plan-journal"
                title="Journal For This Plan"
              >
                {loaderData.journal && (
                  <JournalStack
                    topLevelInfo={topLevelInfo}
                    journals={[loaderData.journal]}
                  />
                )}

                {sortedSubJournals.length > 0 && (
                  <JournalStack
                    topLevelInfo={topLevelInfo}
                    journals={sortedSubJournals}
                  />
                )}
              </SectionCardNew>
            )}
        </NestingAwareBlock>
      </Form>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/time-plans",
  ParamsSchema,
  {
    notFound: (params) => `Could not find time plan #${params.id}!`,
    error: (params) =>
      `There was an error loading time plan #${params.id}. Please try again!`,
  },
);

function inferDefaultSelectedView(workspace: Workspace, timePlan: TimePlan) {
  if (!isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PROJECTS)) {
    return View.MERGED;
  }

  switch (timePlan.period) {
    case RecurringTaskPeriod.DAILY:
    case RecurringTaskPeriod.WEEKLY:
      return View.MERGED;
    case RecurringTaskPeriod.MONTHLY:
    case RecurringTaskPeriod.QUARTERLY:
    case RecurringTaskPeriod.YEARLY:
      return View.BY_PROJECT;
  }
}
