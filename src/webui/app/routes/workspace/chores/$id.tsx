import type { SelectChangeEvent } from "@mui/material";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
  Switch,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { InboxTask, Project } from "jupiter-gen";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  RecurringTaskPeriod,
} from "jupiter-gen";
import { useEffect, useState } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { periodName } from "~/logic/domain/period";
import { getIntent } from "~/logic/intent";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  name: z.string(),
  project: z.string(),
  period: z.nativeEnum(RecurringTaskPeriod),
  eisen: z.nativeEnum(Eisen),
  difficulty: z
    .union([z.nativeEnum(Difficulty), z.literal("default")])
    .optional(),
  actionableFromDay: z.string().optional(),
  actionableFromMonth: z.string().optional(),
  dueAtTime: z.string().optional(),
  dueAtDay: z.string().optional(),
  dueAtMonth: z.string().optional(),
  mustDo: CheckboxAsString,
  skipRule: z.string().optional(),
  startAtDate: z.string().optional(),
  endAtDate: z.string().optional(),
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
    allow_archived: false,
    include_default_project: false,
    include_vacations: false,
    include_projects: true,
    include_inbox_tasks: false,
    include_habits: false,
    include_chores: false,
    include_big_plans: false,
    include_smart_lists: false,
    include_metrics: false,
    include_persons: false,
  });

  try {
    const result = await getLoggedInApiClient(session).chore.loadChore({
      ref_id: { the_id: id },
      allow_archived: true,
    });

    return json({
      chore: result.chore,
      project: result.project,
      inboxTasks: result.inbox_tasks,
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
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "update": {
        await getLoggedInApiClient(session).chore.updateChore({
          ref_id: { the_id: id },
          name: {
            should_change: true,
            value: { the_name: form.name },
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
            value:
              form.difficulty === undefined || form.difficulty === "default"
                ? undefined
                : form.difficulty,
          },
          actionable_from_day: {
            should_change: true,
            value:
              form.actionableFromDay === undefined ||
              form.actionableFromDay === ""
                ? undefined
                : { the_day: parseInt(form.actionableFromDay) },
          },
          actionable_from_month: {
            should_change: true,
            value:
              form.actionableFromMonth === undefined ||
              form.actionableFromMonth === ""
                ? undefined
                : { the_month: parseInt(form.actionableFromMonth) },
          },
          due_at_time: {
            should_change: true,
            value:
              form.dueAtTime === undefined || form.dueAtTime === ""
                ? undefined
                : { the_time: form.dueAtTime },
          },
          due_at_day: {
            should_change: true,
            value:
              form.dueAtDay === undefined || form.dueAtDay === ""
                ? undefined
                : { the_day: parseInt(form.dueAtDay) },
          },
          due_at_month: {
            should_change: true,
            value:
              form.dueAtMonth === undefined || form.dueAtMonth === ""
                ? undefined
                : { the_month: parseInt(form.dueAtMonth) },
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
                : { skip_rule: form.skipRule },
          },
          start_at_date: {
            should_change: true,
            value:
              form.startAtDate === undefined || form.startAtDate === ""
                ? undefined
                : { the_date: form.startAtDate, the_datetime: undefined },
          },
          end_at_date: {
            should_change: true,
            value:
              form.endAtDate === undefined || form.endAtDate === ""
                ? undefined
                : { the_date: form.endAtDate, the_datetime: undefined },
          },
        });

        return redirect(`/workspace/chores/${id}`);
      }

      case "change-project": {
        await getLoggedInApiClient(session).chore.changeChoreProject({
          ref_id: { the_id: id },
          project_ref_id: { the_id: form.project },
        });

        return redirect(`/workspace/chores/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).chore.archiveChore({
          ref_id: { the_id: id },
        });

        return redirect(`/workspace/chores/${id}`);
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

export default function Chore() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.chore.archived;

  const [selectedProject, setSelectedProject] = useState(
    loaderData.project.ref_id.the_id
  );
  const selectedProjectIsDifferentFromCurrent =
    loaderData.project.ref_id.the_id !== selectedProject;

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
        id: it.ref_id.the_id,
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
        id: it.ref_id.the_id,
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
    setSelectedProject(loaderData.project.ref_id.the_id);
  }, [loaderData]);

  return (
    <LeafCard
      key={loaderData.chore.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/chores"
    >
      <GlobalError actionResult={actionData} />
      <Card>
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.chore.name.the_name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="period">Period</InputLabel>
              <Select
                labelId="status"
                name="period"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.chore.gen_params.period}
                label="Period"
              >
                {Object.values(RecurringTaskPeriod).map((s) => (
                  <MenuItem key={s} value={s}>
                    {periodName(s)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/status" />
            </FormControl>

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
                {loaderData.allProjects.map((p: Project) => (
                  <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                    {p.name.the_name}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/project" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="eisen">Eisenhower</InputLabel>
              <Select
                labelId="eisen"
                name="eisen"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.chore.gen_params.eisen}
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
                defaultValue={
                  loaderData.chore.gen_params.difficulty || "default"
                }
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
              <InputLabel id="actionableFromDay">
                Actionable From Day
              </InputLabel>
              <OutlinedInput
                label="Actionable From Day"
                name="actionableFromDay"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.chore.gen_params.actionable_from_day?.the_day
                }
              />
              <FieldError
                actionResult={actionData}
                fieldName="/actionable_from_day"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="actionableFromMonth">
                Actionable From Month
              </InputLabel>
              <OutlinedInput
                label="Actionable From Month"
                name="actionableFromMonth"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.chore.gen_params.actionable_from_month?.the_month
                }
              />
              <FieldError
                actionResult={actionData}
                fieldName="/actionable_from_month"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="dueAtTime">Due At Time</InputLabel>
              <OutlinedInput
                label="Due At Time"
                name="dueAtTime"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.chore.gen_params.due_at_time?.the_time}
              />
              <FieldError actionResult={actionData} fieldName="/due_at_time" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="dueAtDay">Due At Day</InputLabel>
              <OutlinedInput
                label="Due At Day"
                name="dueAtDay"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.chore.gen_params.due_at_day?.the_day}
              />
              <FieldError actionResult={actionData} fieldName="/due_at_day" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="dueAtMonth">Due At Month</InputLabel>
              <OutlinedInput
                label="Due At Month"
                name="dueAtMonth"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.chore.gen_params.due_at_month?.the_month
                }
              />
              <FieldError actionResult={actionData} fieldName="/due_at_month" />
            </FormControl>

            <FormControl fullWidth>
              <FormControlLabel
                control={
                  <Switch
                    name="mustDo"
                    readOnly={!inputsEnabled}
                    defaultChecked={loaderData.chore.must_do}
                  />
                }
                label="Must Do"
              />
              <FieldError actionResult={actionData} fieldName="/must_do" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="skipRule">Skip Rule</InputLabel>
              <OutlinedInput
                label="Skip Rule"
                name="skipRule"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.chore.skip_rule?.skip_rule}
              />
              <FieldError actionResult={actionData} fieldName="/skip_rule" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="startAtDate">Start At Date</InputLabel>
              <OutlinedInput
                type="date"
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
              <InputLabel id="endAtDate">End At Date</InputLabel>
              <OutlinedInput
                type="date"
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

              <FieldError actionResult={actionData} fieldName="/end_at_date" />
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
          </ButtonGroup>
        </CardActions>
      </Card>

      {sortedInboxTasks.length > 0 && (
        <InboxTaskStack
          showLabel
          showOptions={{
            showStatus: true,
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
    </LeafCard>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find chore #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading chore  #${useParams().id}! Please try again!`
);