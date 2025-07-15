import {
  ApiError,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  TimePlanActivityTarget,
} from "@jupiter/webapi-client";
import { FormControl, FormLabel, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  useActionData,
  useNavigation,
  useSearchParams,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { TimePlanActivityFeasabilitySelect } from "~/components/domain/concept/time-plan/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/domain/concept/time-plan/time-plan-activity-kind-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import {
  findTimePlansThatAreActive,
  sortTimePlansNaturally,
} from "~/logic/domain/time-plan";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { TopLevelInfoContext } from "~/top-level-context";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TimePlanStack } from "~/components/domain/concept/time-plan/time-plan-stack";

const ParamsSchema = z.object({});

const QuerySchema = z.object({
  inboxTaskRefId: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("add"),
    targetTimePlanRefIds: z
      .string()
      .transform((s) => (s === "" ? [] : s.split(","))),
    kind: z.nativeEnum(TimePlanActivityKind),
    feasability: z.nativeEnum(TimePlanActivityFeasability),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);

  const [inboxTaskResult, timePlansResult, timePlanActivitiesResult] =
    await Promise.all([
      apiClient.inboxTasks.inboxTaskLoad({
        ref_id: query.inboxTaskRefId,
        allow_archived: false,
      }),
      apiClient.timePlans.timePlanFind({
        allow_archived: false,
        include_notes: false,
        include_planning_tasks: false,
      }),
      apiClient.activity.timePlanActivityFindForTarget({
        allow_archived: false,
        target: TimePlanActivityTarget.INBOX_TASK,
        target_ref_id: query.inboxTaskRefId,
      }),
    ]);

  return json({
    inboxTask: inboxTaskResult.inbox_task,
    timePlans: timePlansResult.entries,
    timePlanActivities: timePlanActivitiesResult.entries,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "add": {
        await apiClient.timePlans.timePlanAssociateInboxTaskWithPlan({
          inbox_task_ref_id: query.inboxTaskRefId,
          time_plan_ref_ids: form.targetTimePlanRefIds,
          kind: form.kind,
          feasability: form.feasability,
        });

        return redirect(`/app/workspace/inbox-tasks/${query.inboxTaskRefId}`);
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

export default function AddInboxTaskToPlans() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();
  const [searchParams] = useSearchParams();

  const inputsEnabled = navigation.state === "idle";

  const alreadyIncludedTimePlanRefIds = new Set(
    loaderData.timePlanActivities.map((tpa) => tpa.time_plan.ref_id),
  );

  const [targetTimePlanRefIds, setTargetTimePlanRefIds] = useState(
    new Set<string>(),
  );

  const activeTimePlans = sortTimePlansNaturally(
    findTimePlansThatAreActive(
      loaderData.timePlans.map((t) => t.time_plan),
      topLevelInfo.today,
    ),
  );
  const allTimePlans = sortTimePlansNaturally(
    loaderData.timePlans.map((t) => t.time_plan),
  );

  return (
    <LeafPanel
      fakeKey={`add-inbox-task-to-plans/${searchParams.get("inboxTaskRefId")}`}
      returnLocation={`/app/workspace/inbox-tasks/${searchParams.get("inboxTaskRefId")}`}
      returnLocationDiscriminator="add-inbox-task-to-plans"
      inputsEnabled={inputsEnabled}
      initialExpansionState={LeafPanelExpansionState.MEDIUM}
    >
      <GlobalError actionResult={actionData} />

      <SectionCard
        id="add-inbox-task-to-plans"
        title="Add to Time Plans"
        actions={
          <SectionActions
            id="add-inbox-task-to-plans"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Add",
                value: "add",
                highlight: true,
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
              defaultValue={TimePlanActivityFeasability.MUST_DO}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/feasability" />
          </FormControl>
        </Stack>

        <TimePlanStack
          id="active-task-time-plans"
          label="Active Time Plans"
          topLevelInfo={topLevelInfo}
          timePlans={activeTimePlans}
          allowSelect
          selectedPredicate={(timePlan) =>
            targetTimePlanRefIds.has(timePlan.ref_id) ||
            alreadyIncludedTimePlanRefIds.has(timePlan.ref_id)
          }
          onClick={(timePlan) => {
            if (alreadyIncludedTimePlanRefIds.has(timePlan.ref_id)) {
              return;
            }
            return setTargetTimePlanRefIds((tpri) =>
              toggleTimePlanRefIds(tpri, timePlan.ref_id),
            );
          }}
        />

        <TimePlanStack
          id="all-time-plans"
          label="All Time Plans"
          topLevelInfo={topLevelInfo}
          timePlans={allTimePlans}
          allowSelect
          selectedPredicate={(timePlan) =>
            targetTimePlanRefIds.has(timePlan.ref_id) ||
            alreadyIncludedTimePlanRefIds.has(timePlan.ref_id)
          }
          onClick={(timePlan) => {
            if (alreadyIncludedTimePlanRefIds.has(timePlan.ref_id)) {
              return;
            }
            return setTargetTimePlanRefIds((tpri) =>
              toggleTimePlanRefIds(tpri, timePlan.ref_id),
            );
          }}
        />

        <input
          name="targetTimePlanRefIds"
          type="hidden"
          value={Array.from(targetTimePlanRefIds).join(",")}
        />
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params, searchParams) =>
    `/app/workspace/inbox-tasks/${searchParams.get("inboxTaskRefId")}`,
  ParamsSchema,
  {
    error: () =>
      `There was an error adding the inbox task to time plans! Please try again!`,
  },
);

function toggleTimePlanRefIds(
  timePlanRefIds: Set<string>,
  refId: string,
): Set<string> {
  const newTimePlanRefIds = new Set(timePlanRefIds);
  if (newTimePlanRefIds.has(refId)) {
    newTimePlanRefIds.delete(refId);
  } else {
    newTimePlanRefIds.add(refId);
  }
  return newTimePlanRefIds;
}
