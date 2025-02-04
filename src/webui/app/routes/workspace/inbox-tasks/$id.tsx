import type {
  BigPlan,
  ProjectSummary,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskSource,
  InboxTaskStatus,
  NoteDomain,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import {
  Autocomplete,
  Box,
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
import {
  json,
  redirect,
  type ActionArgs,
  type LoaderArgs,
} from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultySelect } from "~/components/difficulty-select";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskSourceLink } from "~/components/inbox-task-source-link";
import { InboxTaskStatusBigTag } from "~/components/inbox-task-status-big-tag";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ProjectSelect } from "~/components/project-select";
import { TimeEventInDayBlockStack } from "~/components/time-event-in-day-block-stack";
import { TimePlanActivityList } from "~/components/time-plan-activity-list";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import {
  doesInboxTaskAllowChangingBigPlan,
  doesInboxTaskAllowChangingProject,
  isInboxTaskCoreFieldEditable,
} from "~/logic/domain/inbox-task";
import { allowUserChanges } from "~/logic/domain/inbox-task-source";
import {
  sortInboxTaskTimeEventsNaturally,
  timeEventInDayBlockToTimezone,
} from "~/logic/domain/time-event";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
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
  difficulty: z.nativeEnum(Difficulty),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    allow_archived: false,
    include_workspace: true,
    include_projects: true,
    include_big_plans: true,
  });

  try {
    const result = await apiClient.inboxTasks.inboxTaskLoad({
      ref_id: id,
      allow_archived: true,
    });

    const workspace = summaryResponse.workspace as Workspace;
    let timePlanEntries = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)) {
      const timePlanActivitiesResult =
        await apiClient.activity.timePlanActivityFindForTarget({
          allow_archived: true,
          target: TimePlanActivityTarget.INBOX_TASK,
          target_ref_id: id,
        });
      timePlanEntries = timePlanActivitiesResult.entries;
    }

    return json({
      info: result,
      timePlanEntries: timePlanEntries,
      rootProject: summaryResponse.root_project as ProjectSummary,
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
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
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  const corePropertyEditable = isInboxTaskCoreFieldEditable(form.source);

  try {
    switch (intent) {
      case "mark-done":
      case "mark-not-done":
      case "start":
      case "restart":
      case "block":
      case "stop":
      case "reactivate":
      case "update": {
        let status = form.status;
        if (intent === "mark-done") {
          status = InboxTaskStatus.DONE;
        } else if (intent === "mark-not-done") {
          status = InboxTaskStatus.NOT_DONE;
        } else if (intent === "start") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (intent === "restart") {
          status = InboxTaskStatus.IN_PROGRESS;
        } else if (intent === "block") {
          status = InboxTaskStatus.BLOCKED;
        } else if (intent === "stop") {
          status = allowUserChanges(form.source)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        } else if (intent === "reactivate") {
          status = allowUserChanges(form.source)
            ? InboxTaskStatus.NOT_STARTED
            : InboxTaskStatus.NOT_STARTED_GEN;
        }

        const result = await apiClient.inboxTasks.inboxTaskUpdate({
          ref_id: id,
          name: corePropertyEditable
            ? {
                should_change: true,
                value: form.name,
              }
            : { should_change: false },
          status: {
            should_change: true,
            value: status,
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
                value: form.difficulty,
              }
            : { should_change: false },
          actionable_date: {
            should_change: true,
            value:
              form.actionableDate !== undefined && form.actionableDate !== ""
                ? form.actionableDate
                : undefined,
          },
          due_date: {
            should_change: true,
            value:
              form.dueDate !== undefined && form.dueDate !== ""
                ? form.dueDate
                : undefined,
          },
        });

        if (result.record_score_result) {
          return redirect(`/workspace/inbox-tasks`, {
            headers: {
              "Set-Cookie": await saveScoreAction(result.record_score_result),
            },
          });
        }

        return redirect(`/workspace/inbox-tasks`);
      }

      case "change-project": {
        if (form.project === undefined) {
          throw new Error("Unexpected null project");
        }
        await apiClient.inboxTasks.inboxTaskChangeProject({
          ref_id: id,
          project_ref_id: form.project,
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "associate-with-big-plan": {
        await apiClient.inboxTasks.inboxTaskAssociateWithBigPlan({
          ref_id: id,
          big_plan_ref_id:
            form.bigPlan !== undefined && form.bigPlan !== "none"
              ? form.bigPlan
              : undefined,
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.INBOX_TASK,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/workspace/inbox-tasks/${id}`);
      }

      case "archive": {
        await apiClient.inboxTasks.inboxTaskArchive({
          ref_id: id,
        });

        return redirect(`/workspace/inbox-tasks`);
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function InboxTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const [selectedBigPlan, setSelectedBigPlan] = useState(
    loaderData.info.big_plan
      ? {
          label: loaderData.info.big_plan.name,
          big_plan_id: loaderData.info.big_plan.ref_id,
        }
      : {
          label: "None",
          big_plan_id: "none",
        }
  );
  const selectedBigPlanIsDifferentFromCurrent = loaderData.info.big_plan
    ? loaderData.info.big_plan.ref_id !== selectedBigPlan.big_plan_id
    : selectedBigPlan.big_plan_id !== "none";

  const [selectedProject, setSelectedProject] = useState(
    loaderData.info.project.ref_id
  );
  const [blockedToSelectProject, setBlockedToSelectProject] = useState(false);
  const selectedProjectIsDifferentFromCurrent =
    loaderData.info.project.ref_id !== selectedProject;

  const info = loaderData.info;
  const inboxTask = loaderData.info.inbox_task;

  const inputsEnabled = transition.state === "idle" && !inboxTask.archived;
  const corePropertyEditable = isInboxTaskCoreFieldEditable(inboxTask.source);
  const canChangeProject = doesInboxTaskAllowChangingProject(inboxTask.source);
  const canChangeBigPlan = doesInboxTaskAllowChangingBigPlan(inboxTask.source);

  const inboxTasksByRefId = new Map();
  inboxTasksByRefId.set(
    loaderData.info.inbox_task.ref_id,
    loaderData.info.inbox_task
  );

  const timePlanActivities = loaderData.timePlanEntries?.map(
    (entry) => entry.time_plan_activity
  );
  const timePlansByRefId = new Map();
  if (loaderData.timePlanEntries) {
    for (const entry of loaderData.timePlanEntries) {
      timePlansByRefId.set(entry.time_plan.ref_id, entry.time_plan);
    }
  }

  const timeEventsByRefId = new Map();
  timeEventsByRefId.set(
    `it:${loaderData.info.inbox_task.ref_id}`,
    loaderData.info.time_event_blocks
  );

  const allProjectsById: { [k: string]: ProjectSummary } = {};
  if (
    isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.PROJECTS
    )
  ) {
    for (const project of loaderData.allProjects) {
      allProjectsById[project.ref_id] = project;
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
      allBigPlansById[bigPlan.ref_id] = bigPlan;
    }

    allBigPlansAsOptions = [
      {
        label: "None",
        big_plan_id: "none",
      },
    ].concat(
      loaderData.allBigPlans.map((bp: BigPlan) => ({
        label: bp.name,
        big_plan_id: bp.ref_id,
      }))
    );
  }

  function handleChangeBigPlan(
    e: React.SyntheticEvent,
    { label, big_plan_id }: BigPlanACOption
  ) {
    setSelectedBigPlan({ label, big_plan_id });
    if (big_plan_id === "none") {
      setSelectedProject(loaderData.rootProject.ref_id);
      setBlockedToSelectProject(false);
    } else {
      const projectId = allBigPlansById[big_plan_id].project_ref_id;
      const projectKey = allProjectsById[projectId].ref_id;
      setSelectedProject(projectKey);
      setBlockedToSelectProject(true);
    }
  }

  useEffect(() => {
    // Update states based on loader data. This is necessary because these
    // two are not otherwise updated when the loader data changes. Which happens
    // on a navigation event.
    setSelectedBigPlan(
      loaderData.info.big_plan
        ? {
            label: loaderData.info.big_plan.name,
            big_plan_id: loaderData.info.big_plan.ref_id,
          }
        : {
            label: "None",
            big_plan_id: "none",
          }
    );

    setSelectedProject(loaderData.info.project.ref_id);
  }, [loaderData]);

  const timeEventEntries = loaderData.info.time_event_blocks.map((block) => ({
    time_event_in_tz: timeEventInDayBlockToTimezone(
      block,
      topLevelInfo.user.timezone
    ),
    entry: {
      inbox_task: loaderData.info.inbox_task,
      time_events: [block],
    },
  }));
  const sortedTimeEventEntries =
    sortInboxTaskTimeEventsNaturally(timeEventEntries);

  return (
    <LeafPanel
      key={`inbox-task-${inboxTask.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/inbox-tasks"
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <Box sx={{ display: "flex", flexDirection: "row", gap: "0.25rem" }}>
              <FormControl sx={{ flexGrow: 3 }}>
                <InputLabel id="name">Name</InputLabel>
                <OutlinedInput
                  label="Name"
                  name="name"
                  readOnly={!inputsEnabled || !corePropertyEditable}
                  defaultValue={inboxTask.name}
                />
                <FieldError actionResult={actionData} fieldName="/name" />
                <input type="hidden" name="source" value={inboxTask.source} />
              </FormControl>
              <FormControl sx={{ flexGrow: 1 }}>
                <InboxTaskStatusBigTag status={inboxTask.status} />
                <input type="hidden" name="status" value={inboxTask.status} />
                <FieldError actionResult={actionData} fieldName="/status" />
              </FormControl>
              <InboxTaskSourceLink inboxTaskResult={info} />
            </Box>

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
                      autoHighlight
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
                </>
              )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <FormControl fullWidth>
                <ProjectSelect
                  name="project"
                  label="Project"
                  inputsEnabled={inputsEnabled && corePropertyEditable}
                  disabled={
                    !corePropertyEditable ||
                    blockedToSelectProject ||
                    inboxTask.source === InboxTaskSource.BIG_PLAN
                  }
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
                inputsEnabled={inputsEnabled && corePropertyEditable}
                defaultValue={inboxTask.eisen}
              />
              <FieldError actionResult={actionData} fieldName="/eisen" />
            </FormControl>

            <FormControl fullWidth>
              <FormLabel id="difficulty">Difficulty</FormLabel>
              <DifficultySelect
                name="difficulty"
                inputsEnabled={inputsEnabled && corePropertyEditable}
                defaultValue={inboxTask.difficulty}
              />
              <FieldError actionResult={actionData} fieldName="/difficulty" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="actionableDate" shrink>
                Actionable From {corePropertyEditable ? "[Optional]" : ""}
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
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
              <InputLabel id="dueDate" shrink margin="dense">
                Due At {corePropertyEditable ? "[Optional]" : ""}
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
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
          <Stack direction="column" spacing={2} sx={{ width: "100%" }}>
            {(inboxTask.status === InboxTaskStatus.NOT_STARTED ||
              inboxTask.status === InboxTaskStatus.NOT_STARTED_GEN) && (
              <ButtonGroup fullWidth>
                <Button
                  size="small"
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="mark-done"
                >
                  Mark Done
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="mark-not-done"
                >
                  Mark Not Done
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="start"
                >
                  Start
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="block"
                >
                  Block
                </Button>
              </ButtonGroup>
            )}

            {inboxTask.status === InboxTaskStatus.IN_PROGRESS && (
              <ButtonGroup fullWidth>
                <Button
                  size="small"
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="mark-done"
                >
                  Mark Done
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="mark-not-done"
                >
                  Mark Not Done
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="block"
                >
                  Block
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="stop"
                >
                  Stop
                </Button>
              </ButtonGroup>
            )}

            {inboxTask.status === InboxTaskStatus.BLOCKED && (
              <ButtonGroup fullWidth>
                <Button
                  size="small"
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="mark-done"
                >
                  Mark Done
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="mark-not-done"
                >
                  Mark Not Done
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="restart"
                >
                  Restart
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="stop"
                >
                  Stop
                </Button>
              </ButtonGroup>
            )}

            {(inboxTask.status === InboxTaskStatus.DONE ||
              inboxTask.status === InboxTaskStatus.NOT_DONE) && (
              <ButtonGroup fullWidth>
                <Button
                  size="small"
                  variant="outlined"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="reactivate"
                >
                  Reactivate
                </Button>
              </ButtonGroup>
            )}

            <ButtonGroup fullWidth sx={{ marginLeft: "0px" }}>
              <Button
                size="small"
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
                  size="small"
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
                  size="small"
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
          </Stack>
        </CardActions>
      </Card>

      <Card>
        {!loaderData.info.note && (
          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {loaderData.info.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.info.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.SCHEDULE
      ) && (
        <TimeEventInDayBlockStack
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          title="Time Events"
          createLocation={`/workspace/calendar/time-event/in-day-block/new-for-inbox-task?inboxTaskRefId=${loaderData.info.inbox_task.ref_id}`}
          entries={sortedTimeEventEntries}
        />
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.TIME_PLANS
      ) &&
        timePlanActivities && (
          <SectionCardNew
            id="inbox-task-time-plan-activities"
            title="Time Plan Activities"
          >
            <TimePlanActivityList
              topLevelInfo={topLevelInfo}
              activities={timePlanActivities}
              timePlansByRefId={timePlansByRefId}
              inboxTasksByRefId={inboxTasksByRefId}
              bigPlansByRefId={new Map()}
              activityDoneness={{}}
              timeEventsByRefId={timeEventsByRefId}
              fullInfo={false}
            />
          </SectionCardNew>
        )}
    </LeafPanel>
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
