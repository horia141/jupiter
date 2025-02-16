import type { BigPlan, Workspace } from "@jupiter/webapi-client";
import {
  ApiError,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import FlareIcon from "@mui/icons-material/Flare";
import ViewListIcon from "@mui/icons-material/ViewList";
import {
  Box,
  Divider,
  FormControl,
  FormLabel,
  Stack,
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { BigPlanCard } from "~/components/big-plan-card";

import { makeLeafCatchBoundary } from "~/components/infra/catch-boundary";
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
import { TimePlanActivityFeasabilitySelect } from "~/components/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/time-plan-activity-kind-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
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
  MERGED = "merged",
  BY_PROJECT = "by-project",
}

const ParamsSchema = {
  id: z.string(),
};
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

export async function loader({ request, params }: LoaderArgs) {
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

export async function action({ request, params }: ActionArgs) {
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

        return redirect(`/workspace/time-plans/${id}`);
      }

      case "add-and-override": {
        await apiClient.timePlans.timePlanAssociateWithBigPlans({
          ref_id: id,
          big_plan_ref_ids: form.targetBigPlanRefIds,
          override_existing_dates: true,
          kind: form.kind,
          feasability: form.feasability,
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

    throw error;
  }
}

export default function TimePlanAddFromCurrentBigPlans() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.timePlan.archived;

  const alreadyIncludedBigPlanRefIds = new Set(
    loaderData.activities
      .filter((tpa) => tpa.target === TimePlanActivityTarget.BIG_PLAN)
      .map((tpa) => tpa.target_ref_id)
  );

  const [targetBigPlanRefIds, setTargetBigPlanRefIds] = useState(
    new Set<string>()
  );

  const sortedBigPlans = sortBigPlansNaturally(
    loaderData.bigPlans.map((e) => e.big_plan)
  );

  const entriesByRefId: { [key: string]: BigPlanParent } = {};
  for (const entry of loaderData.bigPlans) {
    entriesByRefId[entry.big_plan.ref_id] = bigPlanFindEntryToParent(entry);
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
      key={`time-plan-${id}/add-from-current-big-plans`}
      returnLocation={`/workspace/time-plans/${id}`}
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

        {selectedView === View.MERGED && (
          <BigPlanList
            topLevelInfo={topLevelInfo}
            bigPlans={sortedBigPlans}
            alreadyIncludedBigPlanRefIds={alreadyIncludedBigPlanRefIds}
            targetBigPlanRefIds={targetBigPlanRefIds}
            bigPlansByRefId={entriesByRefId}
            onSelected={(it) =>
              setTargetBigPlanRefIds((itri) =>
                toggleBigPlanRefIds(itri, it.ref_id)
              )
            }
          />
        )}

        {selectedView === View.BY_PROJECT && (
          <>
            {sortedProjects.map((p) => {
              const theBigPlans = sortedBigPlans.filter(
                (se) => entriesByRefId[se.ref_id]?.project?.ref_id === p.ref_id
              );

              if (theBigPlans.length === 0) {
                return null;
              }

              const fullProjectName = computeProjectHierarchicalNameFromRoot(
                p,
                allProjectsByRefId
              );

              return (
                <Box key={`project-${p.ref_id}`}>
                  <Divider variant="fullWidth">
                    <Typography
                      variant="h6"
                      sx={{
                        maxWidth: "calc(100vw - 2rem)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {fullProjectName}
                    </Typography>
                  </Divider>

                  <BigPlanList
                    topLevelInfo={topLevelInfo}
                    bigPlans={theBigPlans}
                    alreadyIncludedBigPlanRefIds={alreadyIncludedBigPlanRefIds}
                    targetBigPlanRefIds={targetBigPlanRefIds}
                    bigPlansByRefId={entriesByRefId}
                    onSelected={(it) =>
                      setTargetBigPlanRefIds((itri) =>
                        toggleBigPlanRefIds(itri, it.ref_id)
                      )
                    }
                  />
                </Box>
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

export const CatchBoundary = makeLeafCatchBoundary(
  () => `/workspace/time-plans/${useParams().id}`,
  () => `Could not find time plan  #${useParams().id}`
);

export const ErrorBoundary = makeLeafErrorBoundary(
  () => `/workspace/time-plans/${useParams().id}`,
  () =>
    `There was an error loading time plan activity #${
      useParams().id
    }. Please try again!`
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
    <Stack spacing={2} useFlexGap>
      {props.bigPlans.map((bigPlan) => (
        <BigPlanCard
          key={`big-plan-${bigPlan.ref_id}`}
          topLevelInfo={props.topLevelInfo}
          bigPlan={bigPlan}
          compact
          allowSelect
          selected={
            props.alreadyIncludedBigPlanRefIds.has(bigPlan.ref_id) ||
            props.targetBigPlanRefIds.has(bigPlan.ref_id)
          }
          showOptions={{
            showDueDate: true,
            showParent: true,
          }}
          parent={props.bigPlansByRefId[bigPlan.ref_id]}
          onClick={(it) => {
            if (props.alreadyIncludedBigPlanRefIds.has(bigPlan.ref_id)) {
              return;
            }

            props.onSelected(it);
          }}
        />
      ))}
    </Stack>
  );
}

function toggleBigPlanRefIds(
  bigPlanRefIds: Set<string>,
  newRefId: string
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
    return View.MERGED;
  }

  return View.BY_PROJECT;
}
