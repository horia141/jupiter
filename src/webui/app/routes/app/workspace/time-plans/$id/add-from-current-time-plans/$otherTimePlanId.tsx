import type { BigPlan, InboxTask, TimePlan } from "@jupiter/webapi-client";
import {
  ApiError,
  InboxTaskSource,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import { FormControl, FormLabel, Stack } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useNavigation } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityStack } from "~/components/infra/entity-stack";

import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionMultipleSpread,
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { TimePlanActivityCard } from "~/components/time-plan-activity-card";
import { TimePlanActivityFeasabilitySelect } from "~/components/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/time-plan-activity-kind-select";
import { TimePlanCard } from "~/components/time-plan-card";
import { TimePlanStack } from "~/components/time-plan-stack";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import {
  filterActivitiesByTargetStatus,
  sortTimePlanActivitiesNaturally,
} from "~/logic/domain/time-plan-activity";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

import { makeLeafCatchBoundary } from "~/components/infra/catch-boundary";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { StandardDivider } from "~/components/standard-divider";
const ParamsSchema = {
  id: z.string(),
  otherTimePlanId: z.string(),
};
const CommonParamsSchema = {
  targetActivitiesRefIds: z
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
  const { id, otherTimePlanId } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_workspace: true,
  });

  try {
    const workspace = summaryResponse.workspace!;

    const mainResult = await apiClient.timePlans.timePlanLoad({
      ref_id: id,
      allow_archived: false,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });

    const otherResult = await apiClient.timePlans.timePlanLoad({
      ref_id: otherTimePlanId,
      allow_archived: true,
      include_targets: true,
      include_completed_nontarget: false,
      include_other_time_plans: true,
    });

    const otherHigherTimePlanResult = otherResult.higher_time_plan
      ? await apiClient.timePlans.timePlanLoad({
          ref_id: otherResult.higher_time_plan!.ref_id,
          allow_archived: true,
          include_targets: false,
          include_completed_nontarget: false,
          include_other_time_plans: true,
        })
      : null;

    let otherTimeEventResult = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.SCHEDULE)) {
      otherTimeEventResult =
        await apiClient.calendar.calendarLoadForDateAndPeriod({
          right_now: otherResult.time_plan.right_now,
          period: otherResult.time_plan.period,
        });
    }

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
      otherTimeEventForInboxTasks:
        otherTimeEventResult?.entries?.inbox_task_entries || [],
      otherTimeEventForBigPlans: [],
      otherHigherTimePlan: otherResult.higher_time_plan as TimePlan,
      otherPreviousTimePlan: otherResult.previous_time_plan as TimePlan,
      otherHigherTimePlanSubTimePlans:
        otherHigherTimePlanResult?.sub_period_time_plans,
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
  const { id, otherTimePlanId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "add": {
        await apiClient.timePlans.timePlanAssociateWithActivities({
          ref_id: id,
          other_time_plan_ref_id: otherTimePlanId,
          activity_ref_ids: form.targetActivitiesRefIds,
          kind: form.kind,
          feasability: form.feasability,
          override_existing_dates: false,
        });

        return redirect(`/app/workspace/time-plans/${id}`);
      }

      case "add-and-override": {
        await apiClient.timePlans.timePlanAssociateWithActivities({
          ref_id: id,
          other_time_plan_ref_id: otherTimePlanId,
          activity_ref_ids: form.targetActivitiesRefIds,
          kind: form.kind,
          feasability: form.feasability,
          override_existing_dates: true,
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

export default function TimePlanAddFromCurrentTimePlans() {
  const { id, otherTimePlanId } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.mainTimePlan.archived;

  const alreadyIncludedActivities = new Set(
    loaderData.otherActivities
      .filter(
        (s) =>
          loaderData.mainActivities.findIndex(
            (r) => r.target === s.target && r.target_ref_id === s.target_ref_id,
          ) !== -1,
      )
      .map((tpa) => tpa.ref_id),
  );
  const [targetActivitiesRefIds, setTargetActivitiesRefIds] = useState(
    new Set<string>(),
  );

  const otherTargetInboxTasksByRefId = new Map<string, InboxTask>(
    loaderData.otherTargetInboxTasks.map((it) => [it.ref_id, it]),
  );
  const otherTargetBigPlansByRefId = new Map<string, BigPlan>(
    loaderData.otherTargetBigPlans
      ? loaderData.otherTargetBigPlans.map((bp) => [bp.ref_id, bp])
      : [],
  );
  const otherTimeEventsByRefId = new Map();
  for (const e of loaderData.otherTimeEventForInboxTasks) {
    otherTimeEventsByRefId.set(`it:${e.inbox_task.ref_id}`, e.time_events);
  }
  // TODO(horia141): re-enable this when we have time events for big plans.
  // for (const e of loaderData.otherTimeEventForInboxTasks) {
  //   otherTimeEventsByRefId.set(`bp:${e.big_plan.ref_id}`, e.time_events);
  // }

  const filteredOtherActivities = filterActivitiesByTargetStatus(
    loaderData.otherActivities,
    otherTargetInboxTasksByRefId,
    otherTargetBigPlansByRefId,
    loaderData.otherActivityDoneness,
  );
  const sortedOtherActivities = sortTimePlanActivitiesNaturally(
    filteredOtherActivities,
    otherTargetInboxTasksByRefId,
    otherTargetBigPlansByRefId,
  );

  return (
    <LeafPanel
      key={`time-plan-${id}/add-from-current-time-plans-${otherTimePlanId}`}
      returnLocation={`/app/workspace/time-plans/${id}`}
      returnLocationDiscriminator="add-from-current-time-plans"
      inputsEnabled={inputsEnabled}
      initialExpansionState={LeafPanelExpansionState.LARGE}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="time-plan-current-activities"
        title="Current Activities"
        actions={
          <SectionActions
            id="add-from-current-time-plans"
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

        <StandardDivider title="Activities" size="large" />

        <EntityStack>
          {sortedOtherActivities.map((activity) => (
            <TimePlanActivityCard
              key={`time-plan-activity-${activity.ref_id}`}
              topLevelInfo={topLevelInfo}
              activity={activity}
              allowSelect
              selected={
                alreadyIncludedActivities.has(activity.ref_id) ||
                targetActivitiesRefIds.has(activity.ref_id)
              }
              indent={
                activity.target === TimePlanActivityTarget.INBOX_TASK &&
                otherTargetInboxTasksByRefId.get(activity.target_ref_id)
                  ?.source === InboxTaskSource.BIG_PLAN
                  ? 2
                  : 0
              }
              onClick={(a) => {
                if (alreadyIncludedActivities.has(activity.ref_id)) {
                  return;
                }

                setTargetActivitiesRefIds((at) =>
                  toggleActivitiesRefIds(at, activity.ref_id),
                );
              }}
              fullInfo={true}
              timePlansByRefId={new Map()}
              inboxTasksByRefId={otherTargetInboxTasksByRefId}
              bigPlansByRefId={otherTargetBigPlansByRefId}
              activityDoneness={loaderData.otherActivityDoneness}
              timeEventsByRefId={otherTimeEventsByRefId}
            />
          ))}
        </EntityStack>
        <input
          name="targetActivitiesRefIds"
          type="hidden"
          value={Array.from(targetActivitiesRefIds).join(",")}
        />
      </SectionCardNew>

      {loaderData.otherHigherTimePlan && (
        <SectionCardNew
          id="time-plan-higher-time-plan"
          title="Higher Time Plan"
        >
          <TimePlanCard
            topLevelInfo={topLevelInfo}
            timePlan={loaderData.otherHigherTimePlan}
            relativeToTimePlan={loaderData.mainTimePlan}
          />
        </SectionCardNew>
      )}

      {loaderData.otherPreviousTimePlan && (
        <SectionCardNew
          id="time-plan-previous-time-plan"
          title="Previous Time Plan"
        >
          <TimePlanCard
            topLevelInfo={topLevelInfo}
            timePlan={loaderData.otherPreviousTimePlan}
            relativeToTimePlan={loaderData.mainTimePlan}
          />
        </SectionCardNew>
      )}

      {loaderData.otherHigherTimePlanSubTimePlans && (
        <SectionCardNew
          id="time-plan-other-higher-time-plan"
          title="Sub Time Plans"
        >
          <TimePlanStack
            topLevelInfo={topLevelInfo}
            timePlans={loaderData.otherHigherTimePlanSubTimePlans}
            relativeToTimePlan={loaderData.mainTimePlan}
          />
        </SectionCardNew>
      )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeLeafCatchBoundary(
  () => `/app/workspace/time-plans/${useParams().id}`,
  () =>
    `Could not find time plan  #${useParams().id}:#${
      useParams().otherTimePlanId
    }`,
);

export const ErrorBoundary = makeLeafErrorBoundary(
  () => `/app/workspace/time-plans/${useParams().id}`,
  () =>
    `There was an error loading time plan activity #${useParams().id}:#${
      useParams().otherTimePlanId
    }. Please try again!`,
);

function toggleActivitiesRefIds(
  ActivitiesRefIds: Set<string>,
  newRefId: string,
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
