import type {
  BigPlan,
  BigPlanStats,
  TimePlan,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import FlareIcon from "@mui/icons-material/Flare";
import ViewListIcon from "@mui/icons-material/ViewList";
import ViewTimelineIcon from "@mui/icons-material/ViewTimeline";
import { FormControl, FormLabel, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { DateTime } from "luxon";
import { Fragment, useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { BigPlanStack } from "~/components/big-plan-stack";
import { BigPlanTimelineBigScreen } from "~/components/big-plan-timeline-big-screen";
import { BigPlanTimelineSmallScreen } from "~/components/big-plan-timeline-small-screen";
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
import { StandardDivider } from "~/components/standard-divider";
import { TimePlanActivityFeasabilitySelect } from "~/components/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/time-plan-activity-kind-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import type { BigPlanParent } from "~/logic/domain/big-plan";
import {
  bigPlanFindEntryToParent,
  sortBigPlansNaturally,
} from "~/logic/domain/big-plan";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import type { TopLevelInfo } from "~/top-level-context";
import { TopLevelInfoContext } from "~/top-level-context";

enum View {
  LIST_MERGED = "list-merged",
  LIST_BY_PROJECT = "list-by-project",
  TIMELINE_MERGED = "timeline-merged",
  TIMELINE_BY_PROJECT = "timeline-by-project",
}

const ParamsSchema = z.object({
  id: z.string(),
});

const CommonParamsSchema = {
  targetBigPlanRefIds: z
    .string()
    .transform((s) => (s === "" ? [] : s.split(","))),
  kind: z.nativeEnum(TimePlanActivityKind),
  feasability: z.nativeEnum(TimePlanActivityFeasability),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("add"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("add-and-override"),
    ...CommonParamsSchema,
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

    const bigPlansResult = await apiClient.bigPlans.bigPlanFind({
      allow_archived: false,
      include_notes: false,
      include_stats: true,
      filter_just_workable: true,
      include_project: true,
      include_inbox_tasks: false,
    });

    return json({
      allProjects: summaryResponse.projects || undefined,
      timePlan: timePlanResult.time_plan,
      activities: timePlanResult.activities,
      bigPlans: bigPlansResult.entries,
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
      case "add": {
        await apiClient.timePlans.timePlanAssociateWithBigPlans({
          ref_id: id,
          big_plan_ref_ids: form.targetBigPlanRefIds,
          override_existing_dates: false,
          kind: form.kind,
          feasability: form.feasability,
        });

        return redirect(`/app/workspace/time-plans/${id}`);
      }

      case "add-and-override": {
        await apiClient.timePlans.timePlanAssociateWithBigPlans({
          ref_id: id,
          big_plan_ref_ids: form.targetBigPlanRefIds,
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

export default function TimePlanAddFromCurrentBigPlans() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const inputsEnabled =
    navigation.state === "idle" && !loaderData.timePlan.archived;
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const alreadyIncludedBigPlanRefIds = new Set(
    loaderData.activities
      .filter((tpa) => tpa.target === TimePlanActivityTarget.BIG_PLAN)
      .map((tpa) => tpa.target_ref_id),
  );

  const [targetBigPlanRefIds, setTargetBigPlanRefIds] = useState(
    new Set<string>(),
  );

  const sortedBigPlans = sortBigPlansNaturally(
    loaderData.bigPlans.map((e) => e.big_plan),
  );

  const entriesByRefId: { [key: string]: BigPlanParent } = {};
  for (const entry of loaderData.bigPlans) {
    entriesByRefId[entry.big_plan.ref_id] = bigPlanFindEntryToParent(entry);
  }

  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p]),
  );
  const bigPlanStatsByRefId = new Map(
    loaderData.bigPlans.map((b) => [b.big_plan.ref_id, b.stats!]),
  );

  const thisYear = aDateToDate(loaderData.timePlan.right_now).startOf("year");

  const [selectedView, setSelectedView] = useState(
    inferDefaultSelectedView(topLevelInfo.workspace),
  );

  useEffect(() => {
    setSelectedView(inferDefaultSelectedView(topLevelInfo.workspace));
  }, [topLevelInfo]);

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-current-big-plans`}
      returnLocation={`/app/workspace/time-plans/${id}`}
      returnLocationDiscriminator="add-from-current-big-plans"
      inputsEnabled={inputsEnabled}
      initialExpansionState={LeafPanelExpansionState.LARGE}
      allowedExpansionStates={[
        LeafPanelExpansionState.LARGE,
        LeafPanelExpansionState.FULL,
      ]}
    >
      <GlobalError actionResult={actionData} />

      <SectionCardNew
        id="time-plan-current-big-plans"
        title="Current Big Plans"
        actions={
          <SectionActions
            id="add-from-current-big-plans"
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
              FilterFewOptionsCompact(
                "View",
                selectedView,
                [
                  {
                    value: View.LIST_MERGED,
                    text: "List Merged",
                    icon: <ViewListIcon />,
                  },
                  {
                    value: View.LIST_BY_PROJECT,
                    text: "List By Project",
                    icon: <FlareIcon />,
                    gatedOn: WorkspaceFeature.PROJECTS,
                  },
                  {
                    value: View.TIMELINE_MERGED,
                    text: "Timeline Merged",
                    icon: <ViewTimelineIcon />,
                  },
                  {
                    value: View.TIMELINE_BY_PROJECT,
                    text: "Timeline By Project",
                    icon: <ViewTimelineIcon />,
                    gatedOn: WorkspaceFeature.PROJECTS,
                  },
                ],
                (selected) => setSelectedView(selected),
              ),
            ]}
          />
        }
      >
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
              defaultValue={TimePlanActivityFeasability.NICE_TO_HAVE}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/feasability" />
          </FormControl>
        </Stack>

        {selectedView === View.LIST_MERGED && (
          <Fragment>
            <StandardDivider title="All Big Plans" size="large" />
            <BigPlanList
              topLevelInfo={topLevelInfo}
              bigPlans={sortedBigPlans}
              alreadyIncludedBigPlanRefIds={alreadyIncludedBigPlanRefIds}
              targetBigPlanRefIds={targetBigPlanRefIds}
              bigPlansByRefId={entriesByRefId}
              onSelected={(it) =>
                setTargetBigPlanRefIds((itri) => {
                  if (alreadyIncludedBigPlanRefIds.has(it.ref_id)) {
                    return itri;
                  }
                  return toggleBigPlanRefIds(itri, it.ref_id);
                })
              }
            />
          </Fragment>
        )}

        {selectedView === View.LIST_BY_PROJECT && (
          <>
            {sortedProjects.map((p) => {
              const theBigPlans = sortedBigPlans.filter(
                (se) => entriesByRefId[se.ref_id]?.project?.ref_id === p.ref_id,
              );

              if (theBigPlans.length === 0) {
                return null;
              }

              const fullProjectName = computeProjectHierarchicalNameFromRoot(
                p,
                allProjectsByRefId,
              );

              return (
                <Fragment key={`project-${p.ref_id}`}>
                  <StandardDivider title={fullProjectName} size="large" />

                  <BigPlanList
                    topLevelInfo={topLevelInfo}
                    bigPlans={theBigPlans}
                    alreadyIncludedBigPlanRefIds={alreadyIncludedBigPlanRefIds}
                    targetBigPlanRefIds={targetBigPlanRefIds}
                    bigPlansByRefId={entriesByRefId}
                    onSelected={(it) =>
                      setTargetBigPlanRefIds((itri) => {
                        if (alreadyIncludedBigPlanRefIds.has(it.ref_id)) {
                          return itri;
                        }
                        return toggleBigPlanRefIds(itri, it.ref_id);
                      })
                    }
                  />
                </Fragment>
              );
            })}
          </>
        )}

        {selectedView === View.TIMELINE_MERGED && (
          <BigPlanTimeline
            thisYear={thisYear}
            timePlan={loaderData.timePlan}
            bigPlanStatsByRefId={bigPlanStatsByRefId}
            topLevelInfo={topLevelInfo}
            bigPlans={sortedBigPlans}
            alreadyIncludedBigPlanRefIds={alreadyIncludedBigPlanRefIds}
            targetBigPlanRefIds={targetBigPlanRefIds}
            onSelected={(it) =>
              setTargetBigPlanRefIds((itri) => {
                if (alreadyIncludedBigPlanRefIds.has(it.ref_id)) {
                  return itri;
                }
                return toggleBigPlanRefIds(itri, it.ref_id);
              })
            }
          />
        )}

        {selectedView === View.TIMELINE_BY_PROJECT && (
          <>
            {sortedProjects.map((p) => {
              const theBigPlans = sortedBigPlans.filter(
                (se) => entriesByRefId[se.ref_id]?.project?.ref_id === p.ref_id,
              );

              if (theBigPlans.length === 0) {
                return null;
              }

              const fullProjectName = computeProjectHierarchicalNameFromRoot(
                p,
                allProjectsByRefId,
              );

              return (
                <Fragment key={`project-${p.ref_id}`}>
                  <StandardDivider title={fullProjectName} size="large" />

                  <BigPlanTimeline
                    thisYear={thisYear}
                    timePlan={loaderData.timePlan}
                    topLevelInfo={topLevelInfo}
                    bigPlans={theBigPlans}
                    bigPlanStatsByRefId={bigPlanStatsByRefId}
                    alreadyIncludedBigPlanRefIds={alreadyIncludedBigPlanRefIds}
                    targetBigPlanRefIds={targetBigPlanRefIds}
                    onSelected={(it) =>
                      setTargetBigPlanRefIds((itri) => {
                        if (alreadyIncludedBigPlanRefIds.has(it.ref_id)) {
                          return itri;
                        }
                        return toggleBigPlanRefIds(itri, it.ref_id);
                      })
                    }
                  />
                </Fragment>
              );
            })}
          </>
        )}

        <input
          name="targetBigPlanRefIds"
          type="hidden"
          value={Array.from(targetBigPlanRefIds).join(",")}
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

interface BigPlanListProps {
  topLevelInfo: TopLevelInfo;
  bigPlans: Array<BigPlan>;
  alreadyIncludedBigPlanRefIds: Set<string>;
  targetBigPlanRefIds: Set<string>;
  bigPlansByRefId: { [key: string]: BigPlanParent };
  onSelected: (it: BigPlan) => void;
}

function BigPlanList(props: BigPlanListProps) {
  return (
    <BigPlanStack
      topLevelInfo={props.topLevelInfo}
      bigPlans={props.bigPlans}
      selectedPredicate={(it) =>
        props.alreadyIncludedBigPlanRefIds.has(it.ref_id) ||
        props.targetBigPlanRefIds.has(it.ref_id)
      }
      compact
      allowSelect
      showOptions={{
        showDonePct: true,
        showDueDate: true,
        showProject: true,
      }}
      onClick={(it) => {
        props.onSelected(it);
      }}
    />
  );
}

interface BigPlanTimelineProps {
  thisYear: DateTime;
  timePlan: TimePlan;
  topLevelInfo: TopLevelInfo;
  bigPlans: Array<BigPlan>;
  bigPlanStatsByRefId: Map<string, BigPlanStats>;
  alreadyIncludedBigPlanRefIds: Set<string>;
  targetBigPlanRefIds: Set<string>;
  onSelected: (it: BigPlan) => void;
}

function BigPlanTimeline(props: BigPlanTimelineProps) {
  const isBigScreen = useBigScreen();

  if (isBigScreen) {
    return (
      <BigPlanTimelineBigScreen
        thisYear={props.thisYear}
        bigPlans={props.bigPlans}
        bigPlanStatsByRefId={props.bigPlanStatsByRefId}
        dateMarkers={[
          {
            date: props.timePlan.start_date,
            color: "red",
            label: "Start Date",
          },
          {
            date: props.timePlan.end_date,
            color: "blue",
            label: "End Date",
          },
        ]}
        selectedPredicate={(it) =>
          props.alreadyIncludedBigPlanRefIds.has(it.ref_id) ||
          props.targetBigPlanRefIds.has(it.ref_id)
        }
        allowSelect
        onClick={(it) => {
          props.onSelected(it);
        }}
      />
    );
  } else {
    return (
      <BigPlanTimelineSmallScreen
        thisYear={props.thisYear}
        bigPlans={props.bigPlans}
        bigPlanStatsByRefId={props.bigPlanStatsByRefId}
        dateMarkers={[
          {
            date: props.timePlan.start_date,
            color: "red",
            label: "Start Date",
          },
          {
            date: props.timePlan.end_date,
            color: "blue",
            label: "End Date",
          },
        ]}
        selectedPredicate={(it) =>
          props.alreadyIncludedBigPlanRefIds.has(it.ref_id) ||
          props.targetBigPlanRefIds.has(it.ref_id)
        }
        allowSelect
        onClick={(it) => {
          props.onSelected(it);
        }}
      />
    );
  }
}

function toggleBigPlanRefIds(
  bigPlanRefIds: Set<string>,
  newRefId: string,
): Set<string> {
  if (bigPlanRefIds.has(newRefId)) {
    const newBigPlanRefIds = new Set<string>();
    for (const ri of bigPlanRefIds.values()) {
      if (ri === newRefId) {
        continue;
      }
      newBigPlanRefIds.add(ri);
    }
    return newBigPlanRefIds;
  } else {
    const newBigPlanRefIds = new Set<string>();
    for (const ri of bigPlanRefIds.values()) {
      newBigPlanRefIds.add(ri);
    }
    newBigPlanRefIds.add(newRefId);
    return newBigPlanRefIds;
  }
}

function inferDefaultSelectedView(workspace: Workspace) {
  if (!isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.PROJECTS)) {
    return View.TIMELINE_MERGED;
  }

  return View.TIMELINE_BY_PROJECT;
}
