import type { InboxTask, Workspace } from "@jupiter/webapi-client";
import {
  ApiError,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import FlareIcon from "@mui/icons-material/Flare";
import ViewListIcon from "@mui/icons-material/ViewList";
import { Box, Divider, Stack, Typography } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { InboxTaskCard } from "~/components/inbox-task-card";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionMultipleSpread,
  ActionSingle,
  FilterFewOptions,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import type { InboxTaskParent } from "~/logic/domain/inbox-task";
import {
  inboxTaskFindEntryToParent,
  sortInboxTasksByEisenAndDifficulty,
} from "~/logic/domain/inbox-task";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
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

const QuerySchema = {
  bigPlanReason: z.literal("for-big-plan").optional(),
  bigPlanRefId: z.string().optional(),
  timePlanActivityRefId: z.string().optional(),
};

const UpdateFormSchema = {
  intent: z.string(),
  targetInboxTaskRefIds: z
    .string()
    .transform((s) => (s === "" ? [] : s.split(","))),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const query = parseQuery(request, QuerySchema);

  const bigPlanReason = query.bigPlanReason || "standard";

  if (bigPlanReason === "for-big-plan") {
    if (!query.bigPlanRefId) {
      throw new Response("Missing Big Plan Id", { status: 500 });
    }

    if (!query.timePlanActivityRefId) {
      throw new Response("Missing Time Plan Activity Id", { status: 500 });
    }
  }

  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const timePlanResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });

    const inboxTasksResult = await getLoggedInApiClient(
      session
    ).inboxTasks.inboxTaskFind({
      allow_archived: false,
      include_notes: false,
      include_time_event_blocks: false,
      filter_just_workable: true,
      filter_big_plan_ref_ids:
        query.bigPlanRefId !== undefined ? [query.bigPlanRefId] : undefined,
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

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const query = parseQuery(request, QuerySchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    const bigPlanReason = query.bigPlanReason || "standard";

    switch (form.intent) {
      case "add": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithInboxTasks({
          ref_id: id,
          inbox_task_ref_ids: form.targetInboxTaskRefIds,
          override_existing_dates: false,
        });
        break;
      }

      case "add-and-override": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithInboxTasks({
          ref_id: id,
          inbox_task_ref_ids: form.targetInboxTaskRefIds,
          override_existing_dates: true,
        });
        break;
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }

    switch (bigPlanReason) {
      case "for-big-plan": {
        return redirect(
          `/workspace/time-plans/${id}/${query.timePlanActivityRefId as string}`
        );
      }

      case "standard":
        return redirect(`/workspace/time-plans/${id}`);
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
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlan.archived;

  const alreadyIncludedInboxTaskRefIds = new Set(
    loaderData.activities
      .filter((tpa) => tpa.target === TimePlanActivityTarget.INBOX_TASK)
      .map((tpa) => tpa.target_ref_id)
  );

  const [targetInboxTaskRefIds, setTargetInboxTaskRefIds] = useState(
    new Set<string>()
  );

  const sortedInboxTasks = sortInboxTasksByEisenAndDifficulty(
    loaderData.inboxTasks.map((e) => e.inbox_task)
  );

  const entriesByRefId: { [key: string]: InboxTaskParent } = {};
  for (const entry of loaderData.inboxTasks) {
    entriesByRefId[entry.inbox_task.ref_id] = inboxTaskFindEntryToParent(entry);
  }

  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p])
  );

  const [selectedView, setSelectedView] = useState(
    inferDefaultSelectedView(topLevelInfo.workspace)
  );

  useEffect(() => {
    setSelectedView(inferDefaultSelectedView(topLevelInfo.workspace));
  }, [topLevelInfo]);

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-current-inbox-tasks`}
      returnLocation={`/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.LARGE}
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
                    text: "Add And Override Dates",
                    value: "add-and-override",
                  }),
                ],
              }),
              FilterFewOptions(
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
                (selected) => setSelectedView(selected)
              ),
            ]}
          />
        }
      >
        {selectedView === View.MERGED && (
          <InboxTaskList
            topLevelInfo={topLevelInfo}
            inboxTasks={sortedInboxTasks}
            alreadyIncludedInboxTaskRefIds={alreadyIncludedInboxTaskRefIds}
            targetInboxTaskRefIds={targetInboxTaskRefIds}
            inboxTasksByRefId={entriesByRefId}
            onSelected={(it) =>
              setTargetInboxTaskRefIds((itri) =>
                toggleInboxTaskRefIds(itri, it.ref_id)
              )
            }
          />
        )}

        {selectedView === View.BY_PROJECT && (
          <>
            {sortedProjects.map((p) => {
              const theInboxTasks = sortedInboxTasks.filter(
                (se) => entriesByRefId[se.ref_id]?.project?.ref_id === p.ref_id
              );

              if (theInboxTasks.length === 0) {
                return null;
              }

              const fullProjectName = computeProjectHierarchicalNameFromRoot(
                p,
                allProjectsByRefId
              );

              return (
                <Box key={`project-${p.ref_id}`}>
                  <Divider>
                    <Typography variant="h6">{fullProjectName}</Typography>
                  </Divider>

                  <InboxTaskList
                    topLevelInfo={topLevelInfo}
                    inboxTasks={theInboxTasks}
                    alreadyIncludedInboxTaskRefIds={
                      alreadyIncludedInboxTaskRefIds
                    }
                    targetInboxTaskRefIds={targetInboxTaskRefIds}
                    inboxTasksByRefId={entriesByRefId}
                    onSelected={(it) =>
                      setTargetInboxTaskRefIds((itri) =>
                        toggleInboxTaskRefIds(itri, it.ref_id)
                      )
                    }
                  />
                </Box>
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

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find time plan  #${useParams().id}`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${
      useParams().id
    }. Please try again!`
);

interface InboxTaskListProps {
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
          topLevelInfo={props.topLevelInfo}
          inboxTask={inboxTask}
          compact
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
  newRefId: string
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
