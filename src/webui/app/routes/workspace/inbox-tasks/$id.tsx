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
import {
  json,
  redirect,
  type ActionArgs,
  type LoaderArgs,
} from "@remix-run/node";
import { ShouldRevalidateFunction, useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type {
  BigPlan,
  Chore,
  EmailTask,
  Habit,
  Metric,
  Person,
  Project,
  SlackTask,
} from "jupiter-gen";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskSource,
  InboxTaskStatus,
  WorkspaceFeature,
} from "jupiter-gen";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { BigPlanTag } from "~/components/big-plan-tag";
import { ChoreTag } from "~/components/chore-tag";
import { EmailTaskTag } from "~/components/email-task-tag";
import { HabitTag } from "~/components/habit-tag";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { MetricTag } from "~/components/metric-tag";
import { PersonTag } from "~/components/person-tag";
import { SlackTaskTag } from "~/components/slack-task-tag";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import {
  doesInboxTaskAllowChangingBigPlan,
  doesInboxTaskAllowChangingProject,
  isInboxTaskCoreFieldEditable,
} from "~/logic/domain/inbox-task";
import { inboxTaskStatusName } from "~/logic/domain/inbox-task-status";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  source: z.nativeEnum(InboxTaskSource),
  name: z.string(),
  project: z.string().optional(),
  bigPlan: z.string().optional(),
  status: z.nativeEnum(InboxTaskStatus),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.union([z.nativeEnum(Difficulty), z.literal("default")]),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
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
    allow_archived: true,
    include_default_project: true,
    include_projects: true,
    include_big_plans: true,
  });

  try {
    const result = await getLoggedInApiClient(session).inboxTask.loadInboxTask({
      ref_id: { the_id: id },
      allow_archived: true,
    });

    return json({
      info: result,
      defaultProject: summaryResponse.default_project as Project,
      allProjects: summaryResponse.projects as Array<Project>,
      allBigPlans: summaryResponse.big_plans as Array<BigPlan>,
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

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  const corePropertyEditable = isInboxTaskCoreFieldEditable(form.source);

  try {
    switch (intent) {
      case "update": {
        const result = await getLoggedInApiClient(session).inboxTask.updateInboxTask({
          ref_id: { the_id: id },
          name: corePropertyEditable
            ? {
                should_change: true,
                value: { the_name: form.name },
              }
            : { should_change: false },
          status: {
            should_change: true,
            value: form.status,
          },
          eisen: corePropertyEditable
            ? {
                should_change: true,
                value: form.eisen,
              }
            : { should_change: false },
          difficulty: corePropertyEditable
            ? {
                should_change: true,
                value:
                  form.difficulty === "default" ? undefined : form.difficulty,
              }
            : { should_change: false },
          actionable_date: {
            should_change: true,
            value:
              form.actionableDate !== undefined && form.actionableDate !== ""
                ? { the_date: form.actionableDate, the_datetime: undefined }
                : undefined,
          },
          due_date: {
            should_change: true,
            value:
              form.dueDate !== undefined && form.dueDate !== ""
                ? { the_date: form.dueDate, the_datetime: undefined }
                : undefined,
          },
        });

        if (result.record_score_result) {
          return redirect(`/workspace/inbox-tasks/${id}`, {headers: {
            "Set-Cookie": await saveScoreAction(result.record_score_result)
          }});
        }

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "change-project": {
        await getLoggedInApiClient(session).inboxTask.changeInboxTaskProject({
          ref_id: { the_id: id },
          project_ref_id: form.project ? { the_id: form.project } : undefined,
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "associate-with-big-plan": {
        await getLoggedInApiClient(
          session
        ).inboxTask.associateInboxTaskWithBigPlan({
          ref_id: { the_id: id },
          big_plan_ref_id:
            form.bigPlan !== undefined && form.bigPlan !== "none"
              ? { the_id: form.bigPlan }
              : undefined,
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).inboxTask.archiveInboxTask({
          ref_id: { the_id: id },
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
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

type BigPlanACOption = {
  label: string;
  big_plan_id: string;
};

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function InboxTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const [selectedBigPlan, setSelectedBigPlan] = useState(
    loaderData.info.big_plan
      ? {
          label: loaderData.info.big_plan.name.the_name,
          big_plan_id: loaderData.info.big_plan.ref_id.the_id,
        }
      : {
          label: "None",
          big_plan_id: "none",
        }
  );
  const selectedBigPlanIsDifferentFromCurrent = loaderData.info.big_plan
    ? loaderData.info.big_plan.ref_id.the_id !== selectedBigPlan.big_plan_id
    : selectedBigPlan.big_plan_id !== "none";

  const [selectedProject, setSelectedProject] = useState(
    loaderData.info.project.ref_id.the_id
  );
  const [blockedToSelectProject, setBlockedToSelectProject] = useState(false);
  const selectedProjectIsDifferentFromCurrent =
    loaderData.info.project.ref_id.the_id !== selectedProject;

  const info = loaderData.info;
  const inboxTask = loaderData.info.inbox_task;

  const inputsEnabled = transition.state === "idle" && !inboxTask.archived;
  const corePropertyEditable = isInboxTaskCoreFieldEditable(inboxTask.source);
  const canChangeProject = doesInboxTaskAllowChangingProject(inboxTask.source);
  const canChangeBigPlan = doesInboxTaskAllowChangingBigPlan(inboxTask.source);

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

  const allBigPlansById: { [k: string]: BigPlan } = {};
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
      loaderData.allBigPlans.map((bp: BigPlan) => ({
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

  useEffect(() => {
    // Update states based on loader data. This is necessary because these
    // two are not otherwise updated when the loader data changes. Which happens
    // on a navigation event.
    setSelectedBigPlan(
      loaderData.info.big_plan
        ? {
            label: loaderData.info.big_plan.name.the_name,
            big_plan_id: loaderData.info.big_plan.ref_id.the_id,
          }
        : {
            label: "None",
            big_plan_id: "none",
          }
    );

    setSelectedProject(loaderData.info.project.ref_id.the_id);
  }, [loaderData]);

  return (
    <LeafCard
      key={inboxTask.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/inbox-tasks"
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
                readOnly={!inputsEnabled || !corePropertyEditable}
                defaultValue={inboxTask.name.the_name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <input type="hidden" name="source" value={inboxTask.source} />

            <FormControl fullWidth>
              <InputLabel id="status">Status</InputLabel>
              <Select
                labelId="status"
                name="status"
                readOnly={!inputsEnabled}
                defaultValue={inboxTask.status}
                label="Status"
              >
                {Object.values(InboxTaskStatus)
                  .filter((s) => {
                    if (
                      inboxTask.source === InboxTaskSource.USER ||
                      inboxTask.source === InboxTaskSource.BIG_PLAN ||
                      inboxTask.source === InboxTaskSource.SLACK_TASK ||
                      inboxTask.source === InboxTaskSource.EMAIL_TASK
                    ) {
                      return s !== InboxTaskStatus.RECURRING;
                    } else {
                      return s !== InboxTaskStatus.ACCEPTED;
                    }
                  })
                  .map((s) => (
                    <MenuItem key={s} value={s}>
                      {inboxTaskStatusName(s)}
                    </MenuItem>
                  ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/status" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.BIG_PLANS
            ) &&
              (inboxTask.source === InboxTaskSource.USER ||
                inboxTask.source === InboxTaskSource.BIG_PLAN) && (
                <>
                  <FormControl fullWidth>
                    <Autocomplete
                      disablePortal
                      id="bigPlan"
                      options={allBigPlansAsOptions}
                      readOnly={!inputsEnabled}
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
                  {info.big_plan && <BigPlanTag bigPlan={info.big_plan} />}
                </>
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.HABITS
            ) &&
              inboxTask.source === InboxTaskSource.HABIT && (
                <HabitTag habit={info.habit as Habit} />
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.CHORES
            ) &&
              inboxTask.source === InboxTaskSource.CHORE && (
                <ChoreTag chore={info.chore as Chore} />
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PERSONS
            ) &&
              (inboxTask.source === InboxTaskSource.PERSON_CATCH_UP ||
                inboxTask.source === InboxTaskSource.PERSON_BIRTHDAY) && (
                <PersonTag person={info.person as Person} />
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.METRICS
            ) &&
              inboxTask.source === InboxTaskSource.METRIC && (
                <MetricTag metric={info.metric as Metric} />
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.SLACK_TASKS
            ) &&
              inboxTask.source === InboxTaskSource.SLACK_TASK && (
                <SlackTaskTag slackTask={info.slack_task as SlackTask} />
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.EMAIL_TASKS
            ) &&
              inboxTask.source === InboxTaskSource.EMAIL_TASK && (
                <EmailTaskTag emailTask={info.email_task as EmailTask} />
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
                  readOnly={!inputsEnabled}
                  disabled={
                    !corePropertyEditable ||
                    blockedToSelectProject ||
                    inboxTask.source === InboxTaskSource.BIG_PLAN
                  }
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
                readOnly={!inputsEnabled || !corePropertyEditable}
                defaultValue={inboxTask.eisen}
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
                readOnly={!inputsEnabled || !corePropertyEditable}
                defaultValue={inboxTask.difficulty || "default"}
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
                readOnly={!inputsEnabled || !corePropertyEditable}
                defaultValue={
                  inboxTask.actionable_date
                    ? aDateToDate(inboxTask.actionable_date).toFormat(
                        "yyyy-MM-dd"
                      )
                    : undefined
                }
                name="actionableDate"
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
                readOnly={!inputsEnabled || !corePropertyEditable}
                defaultValue={
                  inboxTask.due_date
                    ? aDateToDate(inboxTask.due_date).toFormat("yyyy-MM-dd")
                    : undefined
                }
                name="dueDate"
              />

              <FieldError actionResult={actionData} fieldName="/due_date" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>
            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <Button
                variant="outlined"
                disabled={
                  !inputsEnabled ||
                  !canChangeProject ||
                  !selectedProjectIsDifferentFromCurrent
                }
                type="submit"
                name="intent"
                value="change-project"
              >
                Change Project
              </Button>
            )}
            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.BIG_PLANS
            ) && (
              <Button
                variant="outlined"
                disabled={
                  !inputsEnabled ||
                  !canChangeBigPlan ||
                  !selectedBigPlanIsDifferentFromCurrent
                }
                type="submit"
                name="intent"
                value="associate-with-big-plan"
              >
                Assoc. Big Plan
              </Button>
            )}
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafCard>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find inbox task #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading inbox task #${
      useParams().id
    }! Please try again!`
);
