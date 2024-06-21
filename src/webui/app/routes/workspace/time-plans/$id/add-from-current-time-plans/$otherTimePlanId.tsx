import type { BigPlan, InboxTask, TimePlan } from "@jupiter/webapi-client";
import { ApiError, TimePlanActivityTarget } from "@jupiter/webapi-client";
import { Button } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCard } from "~/components/infra/section-card";
import { TimePlanActivityCard } from "~/components/time-plan-activity-card";
import { TimePlanCard } from "~/components/time-plan-card";
import { TimePlanStack } from "~/components/time-plan-stack";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import {
  filterActivitiesByTargetStatus,
  sortTimePlanActivitiesNaturally,
} from "~/logic/domain/time-plan-activity";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
  otherTimePlanId: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  targetActivitiesRefIds: z
    .string()
    .transform((s) => (s === "" ? [] : s.split(","))),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id, otherTimePlanId } = parseParams(params, ParamsSchema);

  try {
    const mainResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });

    const otherResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: otherTimePlanId,
      allow_archived: true,
      include_targets: true,
      include_completed_nontarget: false,
      include_other_time_plans: true,
    });

    const otherHigherTimePlanResult = await getLoggedInApiClient(
      session
    ).timePlans.timePlanLoad({
      ref_id: otherResult.higher_time_plan!.ref_id,
      allow_archived: true,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: true,
    });

    return json({
      mainTimePlan: mainResult.time_plan,
      mainActivities: mainResult.activities,
      otherTimePlan: otherResult.time_plan,
      otherActivities: otherResult.activities,
      otherTargetInboxTasks: otherResult.target_inbox_tasks as Array<InboxTask>,
      otherTargetBigPlans: otherResult.target_big_plans,
      otherActivityDoneness: otherResult.activity_doneness as Record<
        string,
        boolean
      >,
      otherHigherTimePlan: otherResult.higher_time_plan as TimePlan,
      otherPreviousTimePlan: otherResult.previous_time_plan as TimePlan,
      otherHigherTimePlanSubTimePlans:
        otherHigherTimePlanResult.sub_period_time_plans,
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
  const { id, otherTimePlanId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "add": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithActivities({
          ref_id: id,
          other_time_plan_ref_id: otherTimePlanId,
          activity_ref_ids: form.targetActivitiesRefIds,
          override_existing_dates: false,
        });

        return redirect(`/workspace/time-plans/${id}`);
      }

      case "add-and-override": {
        await getLoggedInApiClient(
          session
        ).timePlans.timePlanAssociateWithActivities({
          ref_id: id,
          other_time_plan_ref_id: otherTimePlanId,
          activity_ref_ids: form.targetActivitiesRefIds,
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

export default function TimePlanAddFromCurrentTimePlans() {
  const { id, otherTimePlanId } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.mainTimePlan.archived;

  const alreadyIncludedActivities = new Set(
    loaderData.otherActivities
      .filter(
        (s) =>
          loaderData.mainActivities.findIndex(
            (r) => r.target === s.target && r.target_ref_id === s.target_ref_id
          ) !== -1
      )
      .map((tpa) => tpa.ref_id)
  );
  const [targetActivitiesRefIds, setTargetActivitiesRefIds] = useState(
    new Set<string>()
  );

  const otherTargetInboxTasksByRefId = new Map<string, InboxTask>(
    loaderData.otherTargetInboxTasks.map((it) => [it.ref_id, it])
  );
  const otherTargetBigPlansByRefId = new Map<string, BigPlan>(
    loaderData.otherTargetBigPlans
      ? loaderData.otherTargetBigPlans.map((bp) => [bp.ref_id, bp])
      : []
  );

  const filteredOtherActivities = filterActivitiesByTargetStatus(
    loaderData.otherActivities,
    otherTargetInboxTasksByRefId,
    otherTargetBigPlansByRefId,
    loaderData.otherActivityDoneness
  );
  const sortedOtherActivities = sortTimePlanActivitiesNaturally(
    filteredOtherActivities,
    otherTargetInboxTasksByRefId,
    otherTargetBigPlansByRefId
  );

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-current-time-plans-${otherTimePlanId}`}
      returnLocation={`/workspace/time-plans/${id}`}
      initialExpansionState={LeafPanelExpansionState.LARGE}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="Current Activities"
        actions={[
          <Button
            key="add"
            variant="contained"
            disabled={!inputsEnabled}
            type="submit"
            name="intent"
            value="add"
          >
            Add
          </Button>,
          <Button
            key="add-and-override"
            variant="outlined"
            disabled={!inputsEnabled}
            type="submit"
            name="intent"
            value="add-and-override"
          >
            Add and Override Dates
          </Button>,
        ]}
      >
        <EntityStack>
          {sortedOtherActivities.map((activity) => (
            <TimePlanActivityCard
              key={`time-plan-activity-${activity.ref_id}`}
              topLevelInfo={topLevelInfo}
              timePlan={loaderData.otherTimePlan}
              activity={activity}
              allowSelect
              selected={
                alreadyIncludedActivities.has(activity.ref_id) ||
                targetActivitiesRefIds.has(activity.ref_id)
              }
              indent={
                activity.target === TimePlanActivityTarget.INBOX_TASK &&
                otherTargetInboxTasksByRefId.get(activity.target_ref_id)
                  ?.big_plan_ref_id
                  ? 2
                  : 0
              }
              onClick={(a) => {
                if (alreadyIncludedActivities.has(activity.ref_id)) {
                  return;
                }

                setTargetActivitiesRefIds((at) =>
                  toggleActivitiesRefIds(at, activity.ref_id)
                );
              }}
              inboxTasksByRefId={otherTargetInboxTasksByRefId}
              bigPlansByRefId={otherTargetBigPlansByRefId}
              activityDoneness={loaderData.otherActivityDoneness}
            />
          ))}
        </EntityStack>

        <input
          name="targetActivitiesRefIds"
          type="hidden"
          value={Array.from(targetActivitiesRefIds).join(",")}
        />
      </SectionCard>

      {loaderData.otherHigherTimePlan && (
        <SectionCard title="Higher Time Plan">
          <TimePlanCard
            topLevelInfo={topLevelInfo}
            timePlan={loaderData.otherHigherTimePlan}
            relativeToTimePlan={loaderData.mainTimePlan}
          />
        </SectionCard>
      )}

      {loaderData.otherPreviousTimePlan && (
        <SectionCard title="Previous Time Plan">
          <TimePlanCard
            topLevelInfo={topLevelInfo}
            timePlan={loaderData.otherPreviousTimePlan}
            relativeToTimePlan={loaderData.mainTimePlan}
          />
        </SectionCard>
      )}

      {loaderData.otherHigherTimePlanSubTimePlans && (
        <SectionCard title="Sub Time Plans">
          <TimePlanStack
            topLevelInfo={topLevelInfo}
            timePlans={loaderData.otherHigherTimePlanSubTimePlans}
          />
        </SectionCard>
      )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () =>
    `Could not find time plan  #${useParams().id}:#${
      useParams().otherTimePlanId
    }`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading time plan activity #${useParams().id}:#${
      useParams().otherTimePlanId
    }. Please try again!`
);

function toggleActivitiesRefIds(
  ActivitiesRefIds: Set<string>,
  newRefId: string
): Set<string> {
  if (ActivitiesRefIds.has(newRefId)) {
    const newActivitiesRefIds = new Set<string>();
    for (const ri of ActivitiesRefIds.values()) {
      if (ri === newRefId) {
        continue;
      }
      newActivitiesRefIds.add(ri);
    }
    return newActivitiesRefIds;
  } else {
    const newActivitiesRefIds = new Set<string>();
    for (const ri of ActivitiesRefIds.values()) {
      newActivitiesRefIds.add(ri);
    }
    newActivitiesRefIds.add(newRefId);
    return newActivitiesRefIds;
  }
}
