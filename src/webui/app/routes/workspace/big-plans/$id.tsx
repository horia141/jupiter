import type {
  InboxTask,
  ProjectSummary,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  BigPlanStatus,
  InboxTaskStatus,
  NoteDomain,
  TimePlanActivityTarget,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import type { SelectChangeEvent } from "@mui/material";
import {
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
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Link,
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { TimePlanActivityList } from "~/components/time-plan-activity-list";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { bigPlanStatusName } from "~/logic/domain/big-plan-status";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
  alert: z.string().optional(),
};

const UpdateFormSchema = {
  intent: z.string(),
  name: z.string(),
  project: z.string(),
  status: z.nativeEnum(BigPlanStatus),
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
    include_workspace: true,
    include_projects: true,
  });

  try {
    const result = await apiClient.bigPlans.bigPlanLoad({
      ref_id: id,
      allow_archived: true,
    });

    const workspace = summaryResponse.workspace as Workspace;
    let timePlanEntries = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)) {
      const timePlanActivitiesResult =
        await apiClient.activity.timePlanActivityFindForTarget({
          allow_archived: true,
          target: TimePlanActivityTarget.BIG_PLAN,
          target_ref_id: id,
        });
      timePlanEntries = timePlanActivitiesResult.entries;
    }

    return json({
      bigPlan: result.big_plan,
      project: result.project,
      inboxTasks: result.inbox_tasks,
      note: result.note,
      timePlanEntries: timePlanEntries,
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
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

  try {
    switch (intent) {
      case "update": {
        const result = await apiClient.bigPlans.bigPlanUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          status: {
            should_change: true,
            value: form.status,
          },
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
          return redirect(`/workspace/big-plans/${id}`, {
            headers: {
              "Set-Cookie": await saveScoreAction(result.record_score_result),
            },
          });
        }

        return redirect(`/workspace/big-plans/${id}`);
      }

      case "change-project": {
        await apiClient.bigPlans.bigPlanChangeProject({
          ref_id: id,
          project_ref_id: form.project,
        });

        return redirect(`/workspace/big-plans/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.BIG_PLAN,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/workspace/big-plans/${id}`);
      }

      case "archive": {
        await apiClient.bigPlans.bigPlanArchive({
          ref_id: id,
        });

        return redirect(`/workspace/big-plans/${id}`);
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function BigPlan() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.bigPlan.archived;

  const bigPlansByRefId = new Map();
  bigPlansByRefId.set(loaderData.bigPlan.ref_id, loaderData.bigPlan);

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

  const [selectedProject, setSelectedProject] = useState(
    loaderData.project.ref_id
  );
  const selectedProjectIsDifferentFromCurrent =
    loaderData.project.ref_id !== selectedProject;

  function handleChangeProject(e: SelectChangeEvent) {
    setSelectedProject(e.target.value);
  }

  const sortedInboxTasks = sortInboxTasksNaturally(loaderData.inboxTasks, {
    dueDateAscending: false,
  });

  const cardActionFetcher = useFetcher();

  function handleCardMarkDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.DONE,
      },
      {
        method: "post",
        action: "/workspace/inbox-tasks/update-status-and-eisen",
      }
    );
  }

  function handleCardMarkNotDone(it: InboxTask) {
    cardActionFetcher.submit(
      {
        id: it.ref_id,
        status: InboxTaskStatus.NOT_DONE,
      },
      {
        method: "post",
        action: "/workspace/inbox-tasks/update-status-and-eisen",
      }
    );
  }

  useEffect(() => {
    // Update states based on loader data. This is necessary because these
    // two are not otherwise updated when the loader data changes. Which happens
    // on a navigation event.
    setSelectedProject(loaderData.project.ref_id);
  }, [loaderData]);

  return (
    <LeafPanel
      key={`big-plan-${loaderData.bigPlan.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={"/workspace/big-plans"}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.bigPlan.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="status">Status</InputLabel>
              <Select
                labelId="status"
                name="status"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.bigPlan.status}
                label="Status"
              >
                {Object.values(BigPlanStatus).map((s) => (
                  <MenuItem key={s} value={s}>
                    {bigPlanStatusName(s)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/status" />
            </FormControl>

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
                  value={selectedProject}
                  onChange={handleChangeProject}
                  label="Project"
                >
                  {loaderData.allProjects.map((p: ProjectSummary) => (
                    <MenuItem key={p.ref_id} value={p.ref_id}>
                      {p.name}
                    </MenuItem>
                  ))}
                </Select>
                <FieldError actionResult={actionData} fieldName="/project" />
              </FormControl>
            )}
            {!isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && <input type="hidden" name="project" value={selectedProject} />}

            <FormControl fullWidth>
              <InputLabel id="actionableDate">Actionable From</InputLabel>
              <OutlinedInput
                type="date"
                label="actionableDate"
                defaultValue={
                  loaderData.bigPlan.actionable_date
                    ? aDateToDate(loaderData.bigPlan.actionable_date).toFormat(
                        "yyyy-MM-dd"
                      )
                    : undefined
                }
                name="actionableDate"
                readOnly={!inputsEnabled}
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
                defaultValue={
                  loaderData.bigPlan.due_date
                    ? aDateToDate(loaderData.bigPlan.due_date).toFormat(
                        "yyyy-MM-dd"
                      )
                    : undefined
                }
                name="dueDate"
                readOnly={!inputsEnabled}
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
                  !inputsEnabled || !selectedProjectIsDifferentFromCurrent
                }
                type="submit"
                name="intent"
                value="change-project"
              >
                Change Project
              </Button>
            )}
          </ButtonGroup>
        </CardActions>
      </Card>

      <Card>
        {!loaderData.note && (
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

        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>

      <EntityActionHeader>
        <Button
          variant="contained"
          disabled={loaderData.bigPlan.archived}
          to={`/workspace/inbox-tasks/new?bigPlanReason=for-big-plan&bigPlanRefId=${loaderData.bigPlan.ref_id}`}
          component={Link}
        >
          New Task
        </Button>
      </EntityActionHeader>

      {sortedInboxTasks.length > 0 && (
        <InboxTaskStack
          topLevelInfo={topLevelInfo}
          showLabel
          showOptions={{
            showStatus: true,
            showEisen: true,
            showDifficulty: true,
            showActionableDate: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Inbox Tasks"
          inboxTasks={sortedInboxTasks}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.TIME_PLANS
      ) &&
        timePlanActivities && (
          <SectionCardNew
            id="big-plan-time-plan-activities"
            title="Time Plan Activities"
          >
            <TimePlanActivityList
              topLevelInfo={topLevelInfo}
              activities={timePlanActivities}
              timePlansByRefId={timePlansByRefId}
              inboxTasksByRefId={new Map()}
              bigPlansByRefId={bigPlansByRefId}
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
  () => `Could not find big plan #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading big plan #${useParams().id}! Please try again!`
);
