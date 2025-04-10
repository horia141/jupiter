import type { InboxTask, Workspace } from "@jupiter/webapi-client";
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
import {
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { Fragment, useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { InboxTaskCard } from "~/components/inbox-task-card";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionMultipleSpread,
  ActionSingle,
  FilterFewOptionsCompact,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { PeriodSelect } from "~/components/period-select";
import { StandardDivider } from "~/components/standard-divider";
import { TimePlanActivityFeasabilitySelect } from "~/components/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/time-plan-activity-kind-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import type { InboxTaskParent } from "~/logic/domain/inbox-task";
import {
  filterInboxTasksForDisplay,
  inboxTaskFindEntryToParent,
  sortInboxTasksByEisenAndDifficulty,
} from "~/logic/domain/inbox-task";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { fixSelectOutputToEnum, selectZod } from "~/logic/select";
import {
  ActionableTime,
  actionableTimeToDateTime,
} from "~/rendering/actionable-time";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import type { TopLevelInfo } from "~/top-level-context";
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
    intent: z.literal("gen"),
    today: z.string(),
    period: selectZod(z.nativeEnum(RecurringTaskPeriod)),
  }),
  z.object({
    intent: z.literal("add"),
    targetInboxTaskRefIds: z
      .string()
      .transform((s) => (s === "" ? [] : s.split(","))),
    kind: z.nativeEnum(TimePlanActivityKind),
    feasability: z.nativeEnum(TimePlanActivityFeasability),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const timePlanResult = await apiClient.timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });

    const inboxTasksResult = await apiClient.inboxTasks.inboxTaskFind({
      allow_archived: false,
      include_notes: false,
      include_time_event_blocks: false,
      filter_just_workable: true,
      filter_just_generated: true,
    });

    return json({
      allProjects: summaryResponse.projects || undefined,
      timePlan: timePlanResult.time_plan,
      activities: timePlanResult.activities,
      inboxTasks: inboxTasksResult.entries,
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "gen": {
        await apiClient.timePlans.timePlanGenForTimePlan({
          today: form.today,
          period: fixSelectOutputToEnum<RecurringTaskPeriod>(form.period),
        });

        return redirect(
          `/app/workspace/time-plans/${id}/add-from-generated-inbox-tasks`,
        );
      }

      case "add": {
        await apiClient.timePlans.timePlanAssociateWithInboxTasks({
          ref_id: id,
          inbox_task_ref_ids: form.targetInboxTaskRefIds,
          override_existing_dates: true,
          kind: form.kind,
          feasability: form.feasability,
        });

        return redirect(`/app/workspace/time-plans/${id}`);
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

export default function TimePlanAddFromCurrentInboxTasks() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.timePlan.archived;

  const alreadyIncludedInboxTaskRefIds = new Set(
    loaderData.activities
      .filter((tpa) => tpa.target === TimePlanActivityTarget.INBOX_TASK)
      .map((tpa) => tpa.target_ref_id),
  );

  const [targetInboxTaskRefIds, setTargetInboxTaskRefIds] = useState(
    new Set<string>(),
  );

  const entriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of loaderData.inboxTasks) {
    entriesByRefId[entry.inbox_task.ref_id] = inboxTaskFindEntryToParent(entry);
  }

  const [selectedView, setSelectedView] = useState(
    inferDefaultSelectedView(topLevelInfo.workspace),
  );
  const [selectedActionableTime, setSelectedActionableTime] = useState(
    ActionableTime.ONE_WEEK,
  );

  const sortedInboxTasks = sortInboxTasksByEisenAndDifficulty(
    loaderData.inboxTasks.map((e) => e.inbox_task),
  );

  const filteredInboxTasks = filterInboxTasksForDisplay(
    sortedInboxTasks,
    entriesByRefId,
    {},
    {
      includeIfNoActionableDate: true,
      actionableDateEnd: actionableTimeToDateTime(
        selectedActionableTime,
        topLevelInfo.user.timezone,
      ),
      includeIfNoDueDate: true,
    },
  );

  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p]),
  );

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  useEffect(() => {
    setSelectedView(inferDefaultSelectedView(topLevelInfo.workspace));
  }, [topLevelInfo]);

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-generated-inbox-tasks`}
      returnLocation={`/app/workspace/time-plans/${id}`}
      returnLocationDiscriminator="add-from-generated-inbox-tasks"
      inputsEnabled={inputsEnabled}
      initialExpansionState={LeafPanelExpansionState.LARGE}
      allowedExpansionStates={[
        LeafPanelExpansionState.LARGE,
        LeafPanelExpansionState.FULL,
      ]}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="time-plan-current-inbox-tasks"
        title="Current Inbox Tasks"
        actions={
          <SectionActions
            id="time-plan-add-from-current-big-plans"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionMultipleSpread({
                actions: [
                  ActionSingle({
                    text: "Add",
                    value: "add",
                    highlight: true,
                  }),
                  ActionSingle({
                    text: "Gen",
                    value: "gen",
                  }),
                ],
              }),
              FilterFewOptionsCompact(
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
              FilterFewOptionsCompact(
                "Actionable",
                selectedActionableTime,
                [
                  {
                    value: ActionableTime.NOW,
                    text: "From Now",
                  },
                  {
                    value: ActionableTime.ONE_WEEK,
                    text: "One Week",
                  },
                  {
                    value: ActionableTime.ONE_MONTH,
                    text: "One Month",
                  },
                ],
                (selected) => setSelectedActionableTime(selected),
              ),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <Stack
            spacing={2}
            useFlexGap
            direction={isBigScreen ? "row" : "column"}
          >
            <FormControl fullWidth>
              <InputLabel id="today" shrink>
                Generation Date
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="Generation Date"
                readOnly={!inputsEnabled}
                disabled={!inputsEnabled}
                defaultValue={loaderData.timePlan.start_date}
                name="today"
              />

              <FieldError actionResult={actionData} fieldName="/today" />
            </FormControl>

            <FormControl fullWidth>
              <PeriodSelect
                labelId="period"
                label="Generation Period"
                name="period"
                inputsEnabled={inputsEnabled}
                defaultValue={[loaderData.timePlan.period]}
              />
              <FieldError actionResult={actionData} fieldName="/period" />
            </FormControl>
          </Stack>

          <Stack
            spacing={2}
            useFlexGap
            direction={isBigScreen ? "row" : "column"}
          >
            <FormControl fullWidth>
              <FormLabel id="kind">Kind</FormLabel>
              <TimePlanActivitKindSelect
                name="kind"
                defaultValue={TimePlanActivityKind.FINISH}
                inputsEnabled={inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/kind" />
            </FormControl>

            <FormControl fullWidth>
              <FormLabel id="feasability">Feasability</FormLabel>
              <TimePlanActivityFeasabilitySelect
                name="feasability"
                defaultValue={TimePlanActivityFeasability.MUST_DO}
                inputsEnabled={inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/feasability" />
            </FormControl>
          </Stack>
        </Stack>

        {selectedView === View.MERGED && (
          <InboxTaskList
            today={today}
            topLevelInfo={topLevelInfo}
            inboxTasks={filteredInboxTasks}
            alreadyIncludedInboxTaskRefIds={alreadyIncludedInboxTaskRefIds}
            targetInboxTaskRefIds={targetInboxTaskRefIds}
            inboxTasksByRefId={entriesByRefId}
            onSelected={(it) =>
              setTargetInboxTaskRefIds((itri) =>
                toggleInboxTaskRefIds(itri, it.ref_id),
              )
            }
          />
        )}

        {selectedView === View.BY_PROJECT && (
          <>
            {sortedProjects.map((p) => {
              const theInboxTasks = filteredInboxTasks.filter(
                (se) => entriesByRefId[se.ref_id]?.project?.ref_id === p.ref_id,
              );

              if (theInboxTasks.length === 0) {
                return null;
              }

              const fullProjectName = computeProjectHierarchicalNameFromRoot(
                p,
                allProjectsByRefId,
              );

              return (
                <Fragment key={`project-${p.ref_id}`}>
                  <StandardDivider title={fullProjectName} size="large" />

                  <InboxTaskList
                    today={today}
                    topLevelInfo={topLevelInfo}
                    inboxTasks={theInboxTasks}
                    alreadyIncludedInboxTaskRefIds={
                      alreadyIncludedInboxTaskRefIds
                    }
                    targetInboxTaskRefIds={targetInboxTaskRefIds}
                    inboxTasksByRefId={entriesByRefId}
                    onSelected={(it) =>
                      setTargetInboxTaskRefIds((itri) =>
                        toggleInboxTaskRefIds(itri, it.ref_id),
                      )
                    }
                  />
                </Fragment>
              );
            })}
          </>
        )}

        <input
          name="targetInboxTaskRefIds"
          type="hidden"
          value={Array.from(targetInboxTaskRefIds).join(",")}
        />
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params) => `/app/workspace/time-plans/${params.id}`,
  ParamsSchema,
  {
    notFound: (params) => `Could not find time plan #${params.id}!`,
    error: (params) =>
      `There was an error loading time plan #${params.id}! Please try again!`,
  },
);

interface InboxTaskListProps {
  today: DateTime;
  topLevelInfo: TopLevelInfo;
  inboxTasks: Array<InboxTask>;
  alreadyIncludedInboxTaskRefIds: Set<string>;
  targetInboxTaskRefIds: Set<string>;
  inboxTasksByRefId: { [key: string]: InboxTaskParent };
  onSelected: (it: InboxTask) => void;
}

function InboxTaskList(props: InboxTaskListProps) {
  return (
    <Stack spacing={2} useFlexGap>
      {props.inboxTasks.map((inboxTask) => (
        <InboxTaskCard
          key={`inbox-task-${inboxTask.ref_id}`}
          today={props.today}
          topLevelInfo={props.topLevelInfo}
          inboxTask={inboxTask}
          allowSelect
          selected={
            props.alreadyIncludedInboxTaskRefIds.has(inboxTask.ref_id) ||
            props.targetInboxTaskRefIds.has(inboxTask.ref_id)
          }
          showOptions={{
            showProject: true,
            showEisen: true,
            showDifficulty: true,
            showDueDate: true,
            showParent: true,
          }}
          parent={props.inboxTasksByRefId[inboxTask.ref_id]}
          onClick={(it) => {
            if (props.alreadyIncludedInboxTaskRefIds.has(inboxTask.ref_id)) {
              return;
            }

            props.onSelected(it);
          }}
        />
      ))}
    </Stack>
  );
}

function toggleInboxTaskRefIds(
  inboxTaskRefIds: Set<string>,
  newRefId: string,
): Set<string> {
  if (inboxTaskRefIds.has(newRefId)) {
    const newInboxTaskRefIds = new Set<string>();
    for (const ri of inboxTaskRefIds.values()) {
      if (ri === newRefId) {
        continue;
      }
      newInboxTaskRefIds.add(ri);
    }
    return newInboxTaskRefIds;
  } else {
    const newInboxTaskRefIds = new Set<string>();
    for (const ri of inboxTaskRefIds.values()) {
      newInboxTaskRefIds.add(ri);
    }
    newInboxTaskRefIds.add(newRefId);
    return newInboxTaskRefIds;
  }
}

function inferDefaultSelectedView(workspace: Workspace) {
  if (!isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PROJECTS)) {
    return View.MERGED;
  }

  return View.BY_PROJECT;
}
