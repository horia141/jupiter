import type { InboxTask, Project } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  NoteDomain,
  RecurringTaskPeriod,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  Switch,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeLeafCatchBoundary } from "~/components/infra/catch-boundary";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";

import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ProjectSelect } from "~/components/project-select";
import { RecurringTaskGenParamsBlock } from "~/components/recurring-task-gen-params-block";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const QuerySchema = {
  inboxTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    project: z.string().optional(),
    period: z.nativeEnum(RecurringTaskPeriod),
    eisen: z.nativeEnum(Eisen),
    difficulty: z.nativeEnum(Difficulty),
    actionableFromDay: z.string().optional(),
    actionableFromMonth: z.string().optional(),
    dueAtDay: z.string().optional(),
    dueAtMonth: z.string().optional(),
    mustDo: CheckboxAsString,
    skipRule: z.string().optional(),
    startAtDate: z.string().optional(),
    endAtDate: z.string().optional(),
  }),
  z.object({
    intent: z.literal("regen"),
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
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const query = parseQuery(request, QuerySchema);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const result = await apiClient.chores.choreLoad({
      ref_id: id,
      allow_archived: true,
      inbox_task_retrieve_offset: query.inboxTasksRetrieveOffset,
    });

    return json({
      chore: result.chore,
      note: result.note,
      project: result.project,
      inboxTasks: result.inbox_tasks,
      inboxTasksTotalCnt: result.inbox_tasks_total_cnt,
      inboxTasksPageSize: result.inbox_tasks_page_size,
      allProjects: summaryResponse.projects as Array<Project>,
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

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.chores.choreUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          project_ref_id: {
            should_change: form.project ? true : false,
            value: form.project,
          },
          period: {
            should_change: true,
            value: form.period,
          },
          eisen: {
            should_change: true,
            value: form.eisen,
          },
          difficulty: {
            should_change: true,
            value: form.difficulty,
          },
          actionable_from_day: {
            should_change: true,
            value:
              form.actionableFromDay === undefined ||
              form.actionableFromDay === ""
                ? undefined
                : parseInt(form.actionableFromDay),
          },
          actionable_from_month: {
            should_change: true,
            value:
              form.actionableFromMonth === undefined ||
              form.actionableFromMonth === ""
                ? undefined
                : parseInt(form.actionableFromMonth),
          },
          due_at_day: {
            should_change: true,
            value:
              form.dueAtDay === undefined || form.dueAtDay === ""
                ? undefined
                : parseInt(form.dueAtDay),
          },
          due_at_month: {
            should_change: true,
            value:
              form.dueAtMonth === undefined || form.dueAtMonth === ""
                ? undefined
                : parseInt(form.dueAtMonth),
          },
          must_do: {
            should_change: true,
            value: form.mustDo,
          },
          skip_rule: {
            should_change: true,
            value:
              form.skipRule === undefined || form.skipRule === ""
                ? undefined
                : form.skipRule,
          },
          start_at_date: {
            should_change: true,
            value:
              form.startAtDate === undefined || form.startAtDate === ""
                ? undefined
                : form.startAtDate,
          },
          end_at_date: {
            should_change: true,
            value:
              form.endAtDate === undefined || form.endAtDate === ""
                ? undefined
                : form.endAtDate,
          },
        });

        return redirect(`/app/workspace/chores`);
      }

      case "regen": {
        await apiClient.chores.choreRegen({
          ref_id: id,
        });

        return redirect(`/app/workspace/chores/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.CHORE,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/chore/${id}`);
      }

      case "archive": {
        await apiClient.chores.choreArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/chores`);
      }

      case "remove": {
        await apiClient.chores.choreRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/chores`);
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

export default function Chore() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.chore.archived;

  const [selectedProject, setSelectedProject] = useState(
    loaderData.project.ref_id
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
        action: "/app/workspace/inbox-tasks/update-status-and-eisen",
      }
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
      key={`chore-{loaderData.chore.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.chore.archived}
      returnLocation="/app/workspace/chores"
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
                defaultValue={loaderData.chore.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
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

            <RecurringTaskGenParamsBlock
              inputsEnabled={inputsEnabled}
              allowSkipRule
              period={loaderData.chore.gen_params.period}
              eisen={loaderData.chore.gen_params.eisen}
              difficulty={loaderData.chore.gen_params.difficulty}
              actionableFromDay={
                loaderData.chore.gen_params.actionable_from_day
              }
              actionableFromMonth={
                loaderData.chore.gen_params.actionable_from_month
              }
              dueAtDay={loaderData.chore.gen_params.due_at_day}
              dueAtMonth={loaderData.chore.gen_params.due_at_month}
              skipRule={loaderData.chore.gen_params.skip_rule}
              actionData={actionData}
            />

            <FormControl fullWidth>
              <FormControlLabel
                control={
                  <Switch
                    name="mustDo"
                    readOnly={!inputsEnabled}
                    defaultChecked={loaderData.chore.must_do}
                  />
                }
                label="Must Do In Vacation"
              />
              <FieldError actionResult={actionData} fieldName="/must_do" />
            </FormControl>

            <Stack spacing={2} direction={isBigScreen ? "row" : "column"}>
              <FormControl fullWidth>
                <InputLabel id="startAtDate" shrink>
                  Start At Date [Optional]
                </InputLabel>
                <OutlinedInput
                  type="date"
                  notched
                  label="startAtDate"
                  defaultValue={
                    loaderData.chore.start_at_date
                      ? aDateToDate(loaderData.chore.start_at_date).toFormat(
                          "yyyy-MM-dd"
                        )
                      : undefined
                  }
                  name="startAtDate"
                  readOnly={!inputsEnabled}
                />

                <FieldError
                  actionResult={actionData}
                  fieldName="/start_at_date"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="endAtDate" shrink>
                  End At Date [Optional]
                </InputLabel>
                <OutlinedInput
                  type="date"
                  notched
                  label="endAtDate"
                  defaultValue={
                    loaderData.chore.end_at_date
                      ? aDateToDate(loaderData.chore.end_at_date).toFormat(
                          "yyyy-MM-dd"
                        )
                      : undefined
                  }
                  name="endAtDate"
                  readOnly={!inputsEnabled}
                />

                <FieldError
                  actionResult={actionData}
                  fieldName="/end_at_date"
                />
              </FormControl>
            </Stack>
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
            <Button
              variant="outlined"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="regen"
            >
              Regen
            </Button>
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

      {sortedInboxTasks.length > 0 && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Inbox Tasks"
          inboxTasks={sortedInboxTasks}
          withPages={{
            retrieveOffsetParamName: "inboxTasksRetrieveOffset",
            totalCnt: loaderData.inboxTasksTotalCnt,
            pageSize: loaderData.inboxTasksPageSize,
          }}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeLeafCatchBoundary(
  "/app/workspace/chores",
  () => `Could not find chore #${useParams().id}!`
);

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/chores",
  () =>
    `There was an error loading chore  #${useParams().id}! Please try again!`
);
