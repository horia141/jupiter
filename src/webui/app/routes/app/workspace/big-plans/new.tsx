import type { ADate, ProjectSummary, TimePlan } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
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
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultySelect } from "~/components/difficulty-select";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { ProjectSelect } from "~/components/project-select";
import { TimePlanActivityFeasabilitySelect } from "~/components/time-plan-activity-feasability-select";
import { TimePlanActivitKindSelect } from "~/components/time-plan-activity-kind-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({});

const QuerySchema = z.object({
  timePlanReason: z.literal("for-time-plan").optional(),
  timePlanRefId: z.string().optional(),
});

const CreateFormSchema = z.object({
  name: z.string(),
  project: z.string().optional(),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.nativeEnum(Difficulty),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
  timePlanActivityKind: z.nativeEnum(TimePlanActivityKind).optional(),
  timePlanActivityFeasability: z
    .nativeEnum(TimePlanActivityFeasability)
    .optional(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);

  const timePlanReason = query.timePlanReason || "standard";

  let associatedTimePlan = null;
  if (timePlanReason === "for-time-plan") {
    if (!query.timePlanRefId) {
      throw new Response("Missing Time Plan Id", { status: 500 });
    }

    const timePlanResult = await apiClient.timePlans.timePlanLoad({
      allow_archived: false,
      ref_id: query.timePlanRefId,
      include_targets: false,
      include_completed_nontarget: false,
      include_other_time_plans: false,
    });

    associatedTimePlan = timePlanResult.time_plan;
  }

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  return json({
    timePlanReason: timePlanReason,
    associatedTimePlan: associatedTimePlan,
    rootProject: summaryResponse.root_project as ProjectSummary,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const timePlanReason = query.timePlanReason || "standard";

    const result = await apiClient.bigPlans.bigPlanCreate({
      name: form.name,
      time_plan_ref_id:
        timePlanReason === "standard"
          ? undefined
          : (query.timePlanRefId as string),
      time_plan_activity_kind: form.timePlanActivityKind,
      time_plan_activity_feasability: form.timePlanActivityFeasability,
      project_ref_id: form.project !== undefined ? form.project : undefined,
      eisen: form.eisen,
      difficulty: form.difficulty,
      actionable_date:
        form.actionableDate !== undefined && form.actionableDate !== ""
          ? form.actionableDate
          : undefined,
      due_date:
        form.dueDate !== undefined && form.dueDate !== ""
          ? form.dueDate
          : undefined,
    });

    switch (timePlanReason) {
      case "standard":
        return redirect(
          `/app/workspace/big-plans/${result.new_big_plan.ref_id}`,
        );

      case "for-time-plan":
        return redirect(
          `/app/workspace/time-plans/${result.new_time_plan_activity?.time_plan_ref_id}/${result.new_time_plan_activity?.ref_id}`,
        );
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function NewBigPlan() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={`big-plans/new`}
      returnLocation="/app/workspace/big-plans"
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        id="big-plan-properties"
        title="Properties"
        actions={
          <SectionActions
            id="big-plan-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Create",
                value: "create",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput label="Name" name="name" readOnly={!inputsEnabled} />
            <FieldError actionResult={actionData} fieldName="/name" />
          </FormControl>

          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS,
          ) && (
            <FormControl fullWidth>
              <ProjectSelect
                name="project"
                label="Project"
                inputsEnabled={inputsEnabled}
                disabled={false}
                allProjects={loaderData.allProjects}
                defaultValue={loaderData.rootProject.ref_id}
              />
              <FieldError actionResult={actionData} fieldName="/project" />
            </FormControl>
          )}

          <FormControl fullWidth>
            <FormLabel id="eisen">Eisenhower</FormLabel>
            <EisenhowerSelect
              name="eisen"
              defaultValue={Eisen.REGULAR}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/eisen" />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="difficulty">Difficulty</FormLabel>
            <DifficultySelect
              name="difficulty"
              defaultValue={Difficulty.EASY}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/difficulty" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="actionableDate" shrink margin="dense">
              Actionable From [Optional]
            </InputLabel>
            <OutlinedInput
              type="date"
              label="actionableDate"
              notched
              name="actionableDate"
              readOnly={!inputsEnabled}
              defaultValue={
                loaderData.timePlanReason === "for-time-plan"
                  ? aDateToDate(
                      (loaderData.associatedTimePlan as TimePlan)
                        .start_date as ADate,
                    ).toFormat("yyyy-MM-dd")
                  : undefined
              }
            />
            <FieldError
              actionResult={actionData}
              fieldName="/actionable_date"
            />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="dueDate" shrink margin="dense">
              Due Date [Optional]
            </InputLabel>
            <OutlinedInput
              type="date"
              label="dueDate"
              notched
              name="dueDate"
              readOnly={!inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/due_date" />
          </FormControl>

          {loaderData.timePlanReason === "for-time-plan" && (
            <>
              <FormControl fullWidth>
                <FormLabel id="timePlanActivityKind">
                  Time Plan Activity Kind
                </FormLabel>
                <TimePlanActivitKindSelect
                  name="timePlanActivityKind"
                  defaultValue={TimePlanActivityKind.FINISH}
                  inputsEnabled={inputsEnabled}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/time_plan_activity_kind"
                />
              </FormControl>

              <FormControl fullWidth>
                <FormLabel id="timePlanActivityFeasability">
                  Time Plan Activity Feasability
                </FormLabel>
                <TimePlanActivityFeasabilitySelect
                  name="timePlanActivityFeasability"
                  defaultValue={TimePlanActivityFeasability.NICE_TO_HAVE}
                  inputsEnabled={inputsEnabled}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/time_plan_activity_feasability"
                />
              </FormControl>
            </>
          )}
        </Stack>
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/big-plans",
  ParamsSchema,
  {
    error: () => `There was an error creating the big plan! Please try again!`,
  },
);
