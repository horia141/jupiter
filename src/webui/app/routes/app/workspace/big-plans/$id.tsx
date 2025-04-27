import type {
  InboxTask,
  ProjectSummary,
  Workspace,
} from "@jupiter/webapi-client";
import {
  ApiError,
  BigPlanStatus,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  NoteDomain,
  TimePlanActivityTarget,
  WorkspaceFeature,
  SyncTarget,
} from "@jupiter/webapi-client";
import {
  Box,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  Link,
  useActionData,
  useFetcher,
  useNavigation,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { BigPlanStatusBigTag } from "~/components/big-plan-status-big-tag";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { ProjectSelect } from "~/components/project-select";
import { TimePlanActivityList } from "~/components/time-plan-activity-list";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { DifficultySelect } from "~/components/difficulty-select";
import {
  SectionActions,
  ActionSingle,
} from "~/components/infra/section-actions";

const ParamsSchema = z.object({
  id: z.string(),
});

const CommonParamsSchema = {
  name: z.string(),
  status: z.nativeEnum(BigPlanStatus),
  project: z.string(),
  eisen: z.nativeEnum(Eisen),
  difficulty: z.nativeEnum(Difficulty),
  actionableDate: z.string().optional(),
  dueDate: z.string().optional(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("mark-done"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("mark-not-done"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("start"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("restart"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("block"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("stop"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("reactivate"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("update"),
    ...CommonParamsSchema,
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
  z.object({
    intent: z.literal("refresh-stats"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "mark-done":
      case "mark-not-done":
      case "start":
      case "restart":
      case "block":
      case "stop":
      case "reactivate":
      case "update": {
        let status = form.status;
        if (form.intent === "mark-done") {
          status = BigPlanStatus.DONE;
        } else if (form.intent === "mark-not-done") {
          status = BigPlanStatus.NOT_DONE;
        } else if (form.intent === "start") {
          status = BigPlanStatus.IN_PROGRESS;
        } else if (form.intent === "restart") {
          status = BigPlanStatus.IN_PROGRESS;
        } else if (form.intent === "block") {
          status = BigPlanStatus.BLOCKED;
        } else if (form.intent === "stop") {
          status = BigPlanStatus.NOT_STARTED;
        } else if (form.intent === "reactivate") {
          status = BigPlanStatus.NOT_STARTED;
        }

        const result = await apiClient.bigPlans.bigPlanUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          status: {
            should_change: true,
            value: status,
          },
          project_ref_id: {
            should_change: true,
            value: form.project,
          },
          eisen: {
            should_change: true,
            value: form.eisen,
          },
          difficulty: {
            should_change: true,
            value: form.difficulty,
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
          return redirect(`/app/workspace/big-plans/${id}`, {
            headers: {
              "Set-Cookie": await saveScoreAction(result.record_score_result),
            },
          });
        }

        return redirect(`/app/workspace/big-plans`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.BIG_PLAN,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/big-plans/${id}`);
      }

      case "archive": {
        await apiClient.bigPlans.bigPlanArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/big-plans`);
      }

      case "remove": {
        await apiClient.bigPlans.bigPlanRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/big-plans`);
      }

      case "refresh-stats": {
        await apiClient.stats.statsDo({
          stats_targets: [SyncTarget.BIG_PLANS],
          filter_big_plan_ref_ids: [id],
          filter_habit_ref_ids: undefined,
          filter_journal_ref_ids: undefined,
        });
        return redirect(`/app/workspace/big-plans/${id}`);
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

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function BigPlan() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.bigPlan.archived;

  const bigPlansByRefId = new Map();
  bigPlansByRefId.set(loaderData.bigPlan.ref_id, loaderData.bigPlan);

  const timePlanActivities = loaderData.timePlanEntries?.map(
    (entry) => entry.time_plan_activity,
  );
  const timePlansByRefId = new Map();
  if (loaderData.timePlanEntries) {
    for (const entry of loaderData.timePlanEntries) {
      timePlansByRefId.set(entry.time_plan.ref_id, entry.time_plan);
    }
  }

  const timeEventsByRefId = new Map();

  const [selectedProject, setSelectedProject] = useState(
    loaderData.project.ref_id,
  );

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
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      },
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
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      },
    );
  }

  useEffect(() => {
    // Update states based on loader data. This is necessary because these
    // two are not otherwise updated when the loader data changes. Which happens
    // on a navigation event.
    setSelectedProject(loaderData.project.ref_id);
  }, [loaderData]);

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`big-plan-${loaderData.bigPlan.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.bigPlan.archived}
      returnLocation={"/app/workspace/big-plans"}
    >
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
                text: "Save",
                value: "update",
                highlight: true,
              }),
              ActionSingle({
                text: "Refresh Stats",
                value: "refresh-stats",
              }),
            ]}
          />
        }
      >
        <GlobalError actionResult={actionData} />
        <Stack spacing={2} useFlexGap>
          <Box sx={{ display: "flex", flexDirection: "row", gap: "0.25rem" }}>
            <FormControl sx={{ flexGrow: 3 }}>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.bigPlan.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>
            <FormControl sx={{ flexGrow: 1 }}>
              <BigPlanStatusBigTag status={loaderData.bigPlan.status} />
              <input
                type="hidden"
                name="status"
                value={loaderData.bigPlan.status}
              />
              <FieldError actionResult={actionData} fieldName="/status" />
            </FormControl>
          </Box>

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
                value={selectedProject}
                onChange={setSelectedProject}
              />
              <FieldError actionResult={actionData} fieldName="/project" />
            </FormControl>
          )}
          {!isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS,
          ) && <input type="hidden" name="project" value={selectedProject} />}

          <FormControl fullWidth>
            <FormLabel id="eisen">Eisenhower</FormLabel>
            <EisenhowerSelect
              name="eisen"
              defaultValue={loaderData.bigPlan.eisen}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/eisen" />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="difficulty">Difficulty</FormLabel>
            <DifficultySelect
              name="difficulty"
              defaultValue={loaderData.bigPlan.difficulty}
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
              notched
              defaultValue={
                loaderData.bigPlan.actionable_date
                  ? aDateToDate(loaderData.bigPlan.actionable_date).toFormat(
                      "yyyy-MM-dd",
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
            <InputLabel id="dueDate" shrink>
              Due At [Optional]
            </InputLabel>
            <OutlinedInput
              type="date"
              notched
              label="dueDate"
              defaultValue={
                loaderData.bigPlan.due_date
                  ? aDateToDate(loaderData.bigPlan.due_date).toFormat(
                      "yyyy-MM-dd",
                    )
                  : undefined
              }
              name="dueDate"
              readOnly={!inputsEnabled}
            />

            <FieldError actionResult={actionData} fieldName="/due_date" />
          </FormControl>
        </Stack>

        <CardActions>
          <Stack direction="column" spacing={2} sx={{ width: "100%" }}>
            {loaderData.bigPlan.status === BigPlanStatus.NOT_STARTED && (
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

            {loaderData.bigPlan.status === BigPlanStatus.IN_PROGRESS && (
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

            {loaderData.bigPlan.status === BigPlanStatus.BLOCKED && (
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

            {(loaderData.bigPlan.status === BigPlanStatus.DONE ||
              loaderData.bigPlan.status === BigPlanStatus.NOT_DONE) && (
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
          </Stack>
        </CardActions>
      </SectionCardNew>

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
          to={`/app/workspace/inbox-tasks/new?bigPlanReason=for-big-plan&bigPlanRefId=${loaderData.bigPlan.ref_id}`}
          component={Link}
        >
          New Task
        </Button>
      </EntityActionHeader>

      {sortedInboxTasks.length > 0 && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
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
        WorkspaceFeature.TIME_PLANS,
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

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/big-plans",
  ParamsSchema,
  {
    notFound: (params) => `Could not find big plan with ID ${params.id}!`,
    error: (params) =>
      `There was an error loading big plan with ID ${params.id}! Please try again!`,
  },
);
