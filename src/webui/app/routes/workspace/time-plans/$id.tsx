import type {
  BigPlan,
  InboxTask,
  TimePlan,
  TimePlanActivity,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  RecurringTaskPeriod,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import FlareIcon from "@mui/icons-material/Flare";
import ViewListIcon from "@mui/icons-material/ViewList";
import {
  Box,
  Button,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Form,
  Outlet,
  useActionData,
  useParams,
  useTransition,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { BigPlanStack } from "~/components/big-plan-stack";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import {
  FilterFewOptions,
  NavMultipleCompact,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { TimePlanActivityCard } from "~/components/time-plan-activity-card";
import { TimePlanStack } from "~/components/time-plan-stack";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { sortTimePlansNaturally } from "~/logic/domain/time-plan";
import { sortTimePlanActivitiesNaturally } from "~/logic/domain/time-plan-activity";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import type { TopLevelInfo } from "~/top-level-context";
import { TopLevelInfoContext } from "~/top-level-context";

enum View {
  MERGED = "merged",
  BY_PROJECT = "by-project",
}

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  rightNow: z.string(),
  period: z.nativeEnum(RecurringTaskPeriod),
};

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const result = await getLoggedInApiClient(session).timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: true,
      include_targets: true,
      include_completed_nontarget: true,
      include_other_time_plans: true,
    });

    return json({
      allProjects: summaryResponse.projects || undefined,
      timePlan: result.time_plan,
      note: result.note,
      activities: result.activities,
      targetInboxTasks: result.target_inbox_tasks as Array<InboxTask>,
      targetBigPlans: result.target_big_plans,
      activityDoneness: result.activity_doneness as Record<string, boolean>,
      completedNontargetInboxTasks:
        result.completed_nontarget_inbox_tasks as Array<InboxTask>,
      completedNontargetBigPlans: result.completed_nottarget_big_plans,
      subPeriodTimePlans: result.sub_period_time_plans as Array<TimePlan>,
      higherTimePlan: result.higher_time_plan as TimePlan,
      previousTimePlan: result.previous_time_plan as TimePlan,
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

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "change-time-config": {
        await getLoggedInApiClient(session).timePlans.timePlanChangeTimeConfig({
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
        return redirect(`/workspace/time-plans/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).timePlans.timePlanArchive({
          ref_id: id,
        });
        return redirect(`/workspace/time-plans/${id}`);
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
  const transition = useTransition();

  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlan.archived;

  const targetInboxTasksByRefId = new Map<string, InboxTask>(
    loaderData.targetInboxTasks.map((it) => [it.ref_id, it])
  );
  const targetBigPlansByRefId = new Map<string, BigPlan>(
    loaderData.targetBigPlans
      ? loaderData.targetBigPlans.map((bp) => [bp.ref_id, bp])
      : []
  );

  const sortedSubTimePlans = sortTimePlansNaturally(
    loaderData.subPeriodTimePlans
  );

  const [selectedView, setSelectedView] = useState(
    inferDefaultSelectedView(topLevelInfo.workspace, loaderData.timePlan)
  );
  useEffect(() => {
    setSelectedView(
      inferDefaultSelectedView(topLevelInfo.workspace, loaderData.timePlan)
    );
  }, [topLevelInfo, loaderData]);

  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p])
  );

  return (
    <BranchPanel
      key={`time-plan-${loaderData.timePlan.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/time-plans"
    >

      <Form method="post">
        <NestingAwareBlock shouldHide={shouldShowALeaf}>
          <GlobalError actionResult={actionData} />
          <SectionCard
            title="Properties"
            actions={[
              <Button
                key="change-time-config"
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="change-time-config"
              >
                Save
              </Button>,
            ]}
          >
            <Stack direction={"row"} spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="rightNow" shrink margin="dense">
                  The Date
                </InputLabel>
                <OutlinedInput
                  type="date"
                  label="rightNow"
                  name="rightNow"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.timePlan.right_now}
                />

                <FieldError actionResult={actionData} fieldName="/right_now" />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="period">Period</InputLabel>
                <Select
                  labelId="status"
                  name="period"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.timePlan.period}
                  label="Period"
                >
                  {Object.values(RecurringTaskPeriod).map((s) => (
                    <MenuItem key={s} value={s}>
                      {periodName(s)}
                    </MenuItem>
                  ))}
                </Select>
                <FieldError actionResult={actionData} fieldName="/status" />
              </FormControl>
            </Stack>
          </SectionCard>
          <SectionCard title="Notes">
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </SectionCard>

          <SectionCardNew
            title="Activities"
            actions={
              <SectionActions
                id="activities"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  NavMultipleCompact(
                    NavSingle(
                      "New Inbox Tasks",
                      `/workspace/inbox-tasks/new?timePlanReason=for-time-plan&timePlanRefId=${loaderData.timePlan.ref_id}`
                    ),
                    NavSingle(
                      "New Big Plan",
                      `/workspace/big-plans/new?timePlanReason=for-time-plan&timePlanRefId=${loaderData.timePlan.ref_id}`,
                      undefined,
                      WorkspaceFeature.BIG_PLANS
                    ),
                    NavSingle(
                      "From Current Inbox Tasks",
                      `/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-inbox-tasks`
                    ),
                    NavSingle(
                      "From Current Big Plans",
                      `/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-big-plans`,
                      undefined,
                      WorkspaceFeature.BIG_PLANS
                    ),
                    NavSingle(
                      "From Time Plans",
                      `/workspace/time-plans/${loaderData.timePlan.ref_id}/add-from-current-time-plans/${loaderData.timePlan.ref_id}`
                    )
                  ),
                  FilterFewOptions(
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
                    (selected) => setSelectedView(selected)
                  ),
                ]}
              />
            }
          >
            {selectedView === View.MERGED && (
              <ActivityList
                topLevelInfo={topLevelInfo}
                timePlan={loaderData.timePlan}
                activities={loaderData.activities}
                inboxTasksByRefId={targetInboxTasksByRefId}
                bigPlansByRefId={targetBigPlansByRefId}
                activityDoneness={loaderData.activityDoneness}
              />
            )}

            {selectedView === View.BY_PROJECT && (
              <>
                {sortedProjects.map((p) => {
                  const theActivities = loaderData.activities.filter((ac) => {
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
                      allProjectsByRefId
                    );

                  return (
                    <Box key={`project-${p.ref_id}`}>
                      <Divider>
                        <Typography variant="h6">{fullProjectName}</Typography>
                      </Divider>

                      <ActivityList
                        topLevelInfo={topLevelInfo}
                        timePlan={loaderData.timePlan}
                        activities={theActivities}
                        inboxTasksByRefId={targetInboxTasksByRefId}
                        bigPlansByRefId={targetBigPlansByRefId}
                        activityDoneness={loaderData.activityDoneness}
                      />
                    </Box>
                  );
                })}
              </>
            )}
          </SectionCardNew>

          {loaderData.completedNontargetInboxTasks.length > 0 && (
            <SectionCard title="Completed & Untracked Inbox Tasks">
              <InboxTaskStack
                topLevelInfo={topLevelInfo}
                showOptions={{
                  showStatus: true,
                  showEisen: true,
                  showDifficulty: true,
                }}
                inboxTasks={loaderData.completedNontargetInboxTasks}
              />
            </SectionCard>
          )}

          {loaderData.completedNontargetBigPlans &&
            loaderData.completedNontargetBigPlans.length > 0 && (
              <SectionCard title="Completed & Untracked Big Plans">
                <BigPlanStack
                  topLevelInfo={topLevelInfo}
                  showOptions={{
                    showStatus: true,
                    showParent: true,
                    showActionableDate: true,
                    showDueDate: true,
                    showHandleMarkDone: false,
                    showHandleMarkNotDone: false,
                  }}
                  bigPlans={loaderData.completedNontargetBigPlans}
                />
              </SectionCard>
            )}

          {sortedSubTimePlans.length > 0 && (
            <SectionCard title="Lower Time Plans">
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={sortedSubTimePlans}
              />
            </SectionCard>
          )}

          {loaderData.higherTimePlan && (
            <SectionCard title="Higher Time Plan">
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={[loaderData.higherTimePlan]}
              />
            </SectionCard>
          )}

          {loaderData.previousTimePlan && (
            <SectionCard title="Previous Time Plan">
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={[loaderData.previousTimePlan]}
              />
            </SectionCard>
          )}
        </NestingAwareBlock>
      </Form>
    
      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </BranchPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find time plan #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan #${useParams().id}. Please try again!`
);

interface ActivityListProps {
  topLevelInfo: TopLevelInfo;
  timePlan: TimePlan;
  activities: Array<TimePlanActivity>;
  inboxTasksByRefId: Map<string, InboxTask>;
  bigPlansByRefId: Map<string, BigPlan>;
  activityDoneness: Record<string, boolean>;
}

function ActivityList(props: ActivityListProps) {
  const sortedActivities = sortTimePlanActivitiesNaturally(
    props.activities,
    props.inboxTasksByRefId,
    props.bigPlansByRefId
  );

  return (
    <EntityStack>
      {sortedActivities.map((entry) => (
        <TimePlanActivityCard
          key={`time-plan-activity-${entry.ref_id}`}
          topLevelInfo={props.topLevelInfo}
          timePlan={props.timePlan}
          activity={entry}
          indent={
            entry.target === TimePlanActivityTarget.INBOX_TASK &&
            props.inboxTasksByRefId.get(entry.target_ref_id)?.big_plan_ref_id
              ? 2
              : 0
          }
          inboxTasksByRefId={props.inboxTasksByRefId}
          bigPlansByRefId={props.bigPlansByRefId}
          activityDoneness={props.activityDoneness}
        />
      ))}
    </EntityStack>
  );
}

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
