import type {
  BigPlan,
  Workspace} from "@jupiter/webapi-client";
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
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { BigPlanCard } from "~/components/big-plan-card";
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
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import type { TopLevelInfo} from "~/top-level-context";
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
  targetBigPlanRefIds: z
    .string()
    .transform((s) => (s === "" ? [] : s.split(","))),
};

export const handle = {
  displayType: DisplayType.LEAF,
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
    const timePlanResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });

    const bigPlansResult = await getLoggedInApiClient(
      session
    ).bigPlans.bigPlanFind({
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
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "add": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithBigPlans({
          ref_id: id,
          big_plan_ref_ids: form.targetBigPlanRefIds,
          override_existing_dates: false,
        });

        return redirect(`/workspace/time-plans/${id}`);
      }

      case "add-and-override": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithBigPlans({
          ref_id: id,
          big_plan_ref_ids: form.targetBigPlanRefIds,
          override_existing_dates: true,
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

  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p])
  );

  const entriesByRefId: { [key: string]: BigPlanParent } = {};
  for (const entry of loaderData.bigPlans) {
    entriesByRefId[entry.big_plan.ref_id] = bigPlanFindEntryToParent(entry);
  }

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
      initialExpansionState={LeafPanelExpansionState.LARGE}
    >
      <GlobalError actionResult={actionData} />

      <SectionCardNew
        title="Current Big Plans"
        actions={
          <SectionActions
            id="add-from-current-big-plans"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionMultipleSpread(
                ActionSingle({
                  text: "Add",
                  value: "add",
                  highlight: true,
                }),
                ActionSingle({
                  text: "Add And Override Dates",
                  value: "add-and-override",
                })
              ),
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
                  <Divider>
                    <Typography variant="h6">{fullProjectName}</Typography>
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

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find time plan  #${useParams().id}`
);

export const ErrorBoundary = makeErrorBoundary(
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
