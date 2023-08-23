import type { SelectChangeEvent } from "@mui/material";
import {
  Autocomplete,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
  TextField,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  ShouldRevalidateFunction,
  useActionData,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import type { BigPlanSummary, Project } from "jupiter-gen";
import { ApiError, Difficulty, Eisen, WorkspaceFeature } from "jupiter-gen";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import {
  BetterFieldError,
  FieldError,
  GlobalError,
} from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const QuerySchema = {
  reason: z.literal("for-big-plan").optional(),
  bigPlanRefId: z.string().optional(),
};

const CreateFormSchema = {
  name: z.string(),
  project: z.string().optional(),
  bigPlan: z.string().optional(),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.union([z.nativeEnum(Difficulty), z.literal("default")]),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
};

type BigPlanACOption = {
  label: string;
  big_plan_id: string;
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);

  const reason = query.reason || "standard";

  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_default_project: true,
    include_projects: true,
    include_big_plans: reason === "standard",
  });

  let ownerBigPlan = null;
  let ownerProject = null;
  if (reason === "for-big-plan" && query.bigPlanRefId) {
    if (!query.bigPlanRefId) {
      throw new Response("Missing Big Plan Id", { status: 500 });
    }

    const bigPlanResult = await getLoggedInApiClient(
      session
    ).bigPlan.loadBigPlan({
      allow_archived: false,
      ref_id: { the_id: query.bigPlanRefId },
    });

    ownerBigPlan = bigPlanResult.big_plan;
    ownerProject = bigPlanResult.project;
  }

  const defaultProject =
    reason === "for-big-plan"
      ? (ownerProject as Project)
      : (summaryResponse.default_project as Project);

  const defaultBigPlan: BigPlanACOption =
    reason === "for-big-plan"
      ? {
          label: ownerBigPlan?.name.the_name as string,
          big_plan_id: query.bigPlanRefId as string,
        }
      : {
          label: "None",
          big_plan_id: "none",
        };

  return json({
    reason: reason,
    defaultProject: defaultProject,
    defaultBigPlan: defaultBigPlan,
    ownerBigPlan: ownerBigPlan,
    allProjects: summaryResponse.projects as Array<Project>,
    allBigPlans:
      reason === "standard"
        ? (summaryResponse.big_plans as Array<BigPlanSummary>)
        : [ownerBigPlan as BigPlanSummary],
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const reason = query.reason || "standard";

    const result = await getLoggedInApiClient(
      session
    ).inboxTask.createInboxTask({
      name: { the_name: form.name },
      project_ref_id:
        form.project !== undefined ? { the_id: form.project } : undefined,
      big_plan_ref_id:
        reason === "standard"
          ? form.bigPlan !== undefined && form.bigPlan !== "none"
            ? { the_id: form.bigPlan }
            : undefined
          : { the_id: query.bigPlanRefId as string },
      eisen: form.eisen,
      difficulty: form.difficulty !== "default" ? form.difficulty : undefined,
      actionable_date:
        form.actionableDate !== undefined && form.actionableDate !== ""
          ? { the_date: form.actionableDate, the_datetime: undefined }
          : undefined,
      due_date:
        form.dueDate !== undefined && form.dueDate !== ""
          ? { the_date: form.dueDate, the_datetime: undefined }
          : undefined,
    });

    switch (reason) {
      case "standard":
        return redirect(
          `/workspace/inbox-tasks/${result.new_inbox_task.ref_id.the_id}`
        );
      case "for-big-plan":
        return redirect(`/workspace/big-plans/${query.bigPlanRefId as string}`);
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
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const [selectedBigPlan, setSelectedBigPlan] = useState(
    loaderData.defaultBigPlan
  );
  const [selectedProject, setSelectedProject] = useState(
    loaderData.defaultProject.ref_id.the_id
  );
  const [blockedToSelectProject, setBlockedToSelectProject] = useState(
    loaderData.reason === "for-big-plan"
  );

  const inputsEnabled = transition.state === "idle";

  const allProjectsById: { [k: string]: Project } = {};
  if (
    isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.PROJECTS
    )
  ) {
    for (const project of loaderData.allProjects) {
      allProjectsById[project.ref_id.the_id] = project;
    }
  }

  const allBigPlansById: { [k: string]: BigPlanSummary } = {};
  let allBigPlansAsOptions: Array<{ label: string; big_plan_id: string }> = [];

  if (
    isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.BIG_PLANS
    )
  ) {
    for (const bigPlan of loaderData.allBigPlans) {
      allBigPlansById[bigPlan.ref_id.the_id] = bigPlan;
    }

    allBigPlansAsOptions = [
      {
        label: "None",
        big_plan_id: "none",
      },
    ].concat(
      loaderData.allBigPlans.map((bp: BigPlanSummary) => ({
        label: bp.name.the_name,
        big_plan_id: bp.ref_id.the_id,
      }))
    );
  }

  function handleChangeBigPlan(
    e: React.SyntheticEvent,
    { label, big_plan_id }: BigPlanACOption
  ) {
    setSelectedBigPlan({ label, big_plan_id });
    if (big_plan_id === "none") {
      setSelectedProject(loaderData.defaultProject.ref_id.the_id);
      setBlockedToSelectProject(false);
    } else {
      const projectId = allBigPlansById[big_plan_id].project_ref_id.the_id;
      const projectKey = allProjectsById[projectId].ref_id.the_id;
      setSelectedProject(projectKey);
      setBlockedToSelectProject(true);
    }
  }

  function handleChangeProject(e: SelectChangeEvent) {
    setSelectedProject(e.target.value);
  }

  return (
    <LeafCard returnLocation="/workspace/inbox-tasks">
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
              WorkspaceFeature.BIG_PLANS
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="bigPlan"
                  options={allBigPlansAsOptions}
                  readOnly={!inputsEnabled || loaderData.reason !== "standard"}
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
              WorkspaceFeature.PROJECTS
            ) && (
              <FormControl fullWidth>
                <InputLabel id="project">Project</InputLabel>
                <Select
                  labelId="project"
                  name="project"
                  readOnly={!inputsEnabled || blockedToSelectProject}
                  value={selectedProject}
                  onChange={handleChangeProject}
                  label="Project"
                >
                  {loaderData.allProjects.map((p: Project) => (
                    <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                      {p.name.the_name}
                    </MenuItem>
                  ))}
                </Select>
                <FieldError
                  actionResult={actionData}
                  fieldName="/project_key"
                />
              </FormControl>
            )}

            <FormControl fullWidth>
              <InputLabel id="eisen">Eisenhower</InputLabel>
              <Select
                labelId="eisen"
                name="eisen"
                readOnly={!inputsEnabled}
                defaultValue={Eisen.REGULAR}
                label="Eisen"
              >
                {Object.values(Eisen).map((e) => (
                  <MenuItem key={e} value={e}>
                    {eisenName(e)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/eisen" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="difficulty">Difficulty</InputLabel>
              <Select
                labelId="difficulty"
                name="difficulty"
                readOnly={!inputsEnabled}
                defaultValue={"default"}
                label="Difficulty"
              >
                <MenuItem value="default">Default</MenuItem>
                {Object.values(Difficulty).map((e) => (
                  <MenuItem key={e} value={e}>
                    {difficultyName(e)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/difficulty" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="actionableDate">Actionable From</InputLabel>
              <OutlinedInput
                type="date"
                label="actionableDate"
                readOnly={!inputsEnabled}
                name="actionableDate"
                defaultValue={
                  loaderData.reason === "for-big-plan" &&
                  loaderData.ownerBigPlan?.actionable_date
                    ? aDateToDate(
                        loaderData.ownerBigPlan.actionable_date
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
              <InputLabel id="dueDate">Due At</InputLabel>
              <OutlinedInput
                type="date"
                label="dueDate"
                readOnly={!inputsEnabled}
                name="dueDate"
                defaultValue={
                  loaderData.reason === "for-big-plan" &&
                  loaderData.ownerBigPlan?.due_date
                    ? aDateToDate(loaderData.ownerBigPlan.due_date).toFormat(
                        "yyyy-MM-dd"
                      )
                    : undefined
                }
              />

              <FieldError actionResult={actionData} fieldName="/due_date" />
            </FormControl>
          </Stack>
        </CardContent>
        <CardActions>
          <ButtonGroup>
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the inbox task! Please try again!`
);
