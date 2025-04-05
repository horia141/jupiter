import type {
  ADate,
  BigPlanSummary,
  Project,
  ProjectSummary,
  TimePlan,
} from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  TimePlanActivityFeasability,
  TimePlanActivityKind,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import {
  Autocomplete,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  TextField,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultySelect } from "~/components/difficulty-select";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import {
  BetterFieldError,
  FieldError,
  GlobalError,
} from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
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
  bigPlanReason: z.literal("for-big-plan").optional(),
  bigPlanRefId: z.string().optional(),
  parentTimePlanActivityRefId: z.string().optional(),
});

const CreateFormSchema = z.object({
  name: z.string(),
  project: z.string().optional(),
  bigPlan: z.string().optional(),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.nativeEnum(Difficulty),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
  timePlanActivityKind: z.nativeEnum(TimePlanActivityKind).optional(),
  timePlanActivityFeasability: z
    .nativeEnum(TimePlanActivityFeasability)
    .optional(),
});

type BigPlanACOption = {
  label: string;
  big_plan_id: string;
};

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

  const bigPlanReason = query.bigPlanReason || "standard";

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
    include_big_plans: bigPlanReason === "standard",
  });

  let ownerBigPlan = null;
  let ownerProject = null;
  if (bigPlanReason === "for-big-plan") {
    if (!query.bigPlanRefId) {
      throw new Response("Missing Big Plan Id", { status: 500 });
    }

    const bigPlanResult = await apiClient.bigPlans.bigPlanLoad({
      allow_archived: false,
      ref_id: query.bigPlanRefId,
    });

    ownerBigPlan = bigPlanResult.big_plan;
    ownerProject = bigPlanResult.project;
  }

  const defaultProject =
    bigPlanReason === "for-big-plan"
      ? (ownerProject as ProjectSummary)
      : (summaryResponse.root_project as ProjectSummary);

  const defaultBigPlan: BigPlanACOption =
    bigPlanReason === "for-big-plan"
      ? {
          label: ownerBigPlan?.name as string,
          big_plan_id: query.bigPlanRefId as string,
        }
      : {
          label: "None",
          big_plan_id: "none",
        };

  return json({
    timePlanReason: timePlanReason,
    bigPlanReason: bigPlanReason,
    associatedTimePlan: associatedTimePlan,
    defaultProject: defaultProject,
    defaultBigPlan: defaultBigPlan,
    ownerBigPlan: ownerBigPlan,
    allProjects: summaryResponse.projects as Array<Project>,
    allBigPlans:
      bigPlanReason === "standard"
        ? (summaryResponse.big_plans as Array<BigPlanSummary>)
        : [ownerBigPlan as BigPlanSummary],
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const query = parseQuery(request, QuerySchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const timePlanReason = query.timePlanReason || "standard";
    const bigPlanReason = query.bigPlanReason || "standard";

    const result = await apiClient.inboxTasks.inboxTaskCreate({
      name: form.name,
      time_plan_ref_id:
        timePlanReason === "standard"
          ? undefined
          : (query.timePlanRefId as string),
      time_plan_activity_kind: form.timePlanActivityKind,
      time_plan_activity_feasability: form.timePlanActivityFeasability,
      project_ref_id: form.project,
      big_plan_ref_id:
        bigPlanReason === "standard"
          ? form.bigPlan !== undefined && form.bigPlan !== "none"
            ? form.bigPlan
            : undefined
          : (query.bigPlanRefId as string),
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
      case "for-time-plan":
        switch (bigPlanReason) {
          case "for-big-plan":
            return redirect(
              `/app/workspace/time-plans/${query.timePlanRefId}/${query.parentTimePlanActivityRefId}`,
            );
          case "standard":
            return redirect(
              `/app/workspace/time-plans/${result.new_time_plan_activity?.time_plan_ref_id}/${result.new_time_plan_activity?.ref_id}`,
            );
        }
        break;

      case "standard":
        switch (bigPlanReason) {
          case "for-big-plan":
            return redirect(
              `/app/workspace/big-plans/${query.bigPlanRefId as string}`,
            );

          case "standard":
            return redirect(
              `/app/workspace/inbox-tasks/${result.new_inbox_task.ref_id}`,
            );
        }
        break;
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

export default function NewInboxTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const [selectedBigPlan, setSelectedBigPlan] = useState(
    loaderData.defaultBigPlan,
  );
  const [selectedProject, setSelectedProject] = useState(
    loaderData.defaultProject.ref_id,
  );
  const [blockedToSelectProject, setBlockedToSelectProject] = useState(
    loaderData.bigPlanReason === "for-big-plan",
  );

  const inputsEnabled = navigation.state === "idle";

  const allProjectsById: { [k: string]: Project } = {};
  if (
    isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.PROJECTS,
    )
  ) {
    for (const project of loaderData.allProjects) {
      allProjectsById[project.ref_id] = project;
    }
  }

  const allBigPlansById: { [k: string]: BigPlanSummary } = {};
  let allBigPlansAsOptions: Array<{ label: string; big_plan_id: string }> = [];

  if (
    isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.BIG_PLANS,
    )
  ) {
    for (const bigPlan of loaderData.allBigPlans) {
      allBigPlansById[bigPlan.ref_id] = bigPlan;
    }

    allBigPlansAsOptions = [
      {
        label: "None",
        big_plan_id: "none",
      },
    ].concat(
      loaderData.allBigPlans.map((bp: BigPlanSummary) => ({
        label: bp.name,
        big_plan_id: bp.ref_id,
      })),
    );
  }

  function handleChangeBigPlan(
    e: React.SyntheticEvent,
    { label, big_plan_id }: BigPlanACOption,
  ) {
    setSelectedBigPlan({ label, big_plan_id });

    if (
      isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.PROJECTS,
      )
    ) {
      if (big_plan_id === "none") {
        setSelectedProject(loaderData.defaultProject.ref_id);
        setBlockedToSelectProject(false);
      } else {
        const projectId = allBigPlansById[big_plan_id].project_ref_id;
        const projectKey = allProjectsById[projectId].ref_id;
        setSelectedProject(projectKey);
        setBlockedToSelectProject(true);
      }
    }
  }

  return (
    <LeafPanel
      key={"inbox-tasks/new"}
      returnLocation="/app/workspace/inbox-tasks"
      inputsEnabled={inputsEnabled}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                {...BetterFieldError({
                  actionResult: actionData,
                  fieldName: "/name",
                })}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.BIG_PLANS,
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="bigPlan"
                  options={allBigPlansAsOptions}
                  readOnly={
                    !inputsEnabled || loaderData.bigPlanReason !== "standard"
                  }
                  value={selectedBigPlan}
                  disableClearable={true}
                  onChange={handleChangeBigPlan}
                  isOptionEqualToValue={(o, v) =>
                    o.big_plan_id === v.big_plan_id
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Big Plan" />
                  )}
                />

                <FieldError
                  actionResult={actionData}
                  fieldName="/big_plan_ref_id"
                />

                <input
                  type="hidden"
                  name="bigPlan"
                  value={selectedBigPlan.big_plan_id}
                />
              </FormControl>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS,
            ) && (
              <FormControl fullWidth>
                <ProjectSelect
                  name="project"
                  label="Project"
                  inputsEnabled={inputsEnabled && !blockedToSelectProject}
                  disabled={false}
                  allProjects={loaderData.allProjects}
                  value={selectedProject}
                  onChange={setSelectedProject}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/project_ref_id"
                />
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
              <InputLabel id="actionableDate" shrink>
                Actionable From [Optional]
              </InputLabel>
              <OutlinedInput
                type="date"
                label="actionableDate"
                readOnly={!inputsEnabled}
                name="actionableDate"
                notched
                defaultValue={
                  loaderData.timePlanReason === "for-time-plan"
                    ? aDateToDate(
                        (loaderData.associatedTimePlan as TimePlan)
                          .start_date as ADate,
                      ).toFormat("yyyy-MM-dd")
                    : loaderData.bigPlanReason === "for-big-plan" &&
                        loaderData.ownerBigPlan?.actionable_date
                      ? aDateToDate(
                          loaderData.ownerBigPlan.actionable_date,
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
              <InputLabel id="dueDate" shrink>
                Due At [Optional]
              </InputLabel>
              <OutlinedInput
                type="date"
                label="dueDate"
                readOnly={!inputsEnabled}
                notched
                name="dueDate"
                defaultValue={
                  loaderData.timePlanReason === "for-time-plan"
                    ? aDateToDate(
                        (loaderData.associatedTimePlan as TimePlan)
                          .end_date as ADate,
                      ).toFormat("yyyy-MM-dd")
                    : loaderData.bigPlanReason === "for-big-plan" &&
                        loaderData.ownerBigPlan?.due_date
                      ? aDateToDate(loaderData.ownerBigPlan.due_date).toFormat(
                          "yyyy-MM-dd",
                        )
                      : ""
                }
              />

              <FieldError actionResult={actionData} fieldName="/due_date" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.TIME_PLANS,
            ) &&
              loaderData.timePlanReason === "for-time-plan" && (
                <>
                  <FormControl fullWidth>
                    <FormLabel id="timePlanActivityKind">Kind</FormLabel>
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
                      Feasability
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
        </CardContent>
        <CardActions>
          <ButtonGroup>
            <Button
              id="inbox-task-create"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
            >
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/inbox-tasks",
  ParamsSchema,
  {
    error: () =>
      `There was an error creating the inbox task! Please try again!`,
  },
);
