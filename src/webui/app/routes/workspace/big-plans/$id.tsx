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
import {
  Link,
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { InboxTask, Project } from "jupiter-gen";
import { ApiError, BigPlanStatus, InboxTaskStatus } from "jupiter-gen";
import { useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { bigPlanStatusName } from "~/logic/domain/big-plan-status";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
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
  status: z.nativeEnum(BigPlanStatus),
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
    include_projects: true,
  });

  try {
    const result = await getLoggedInApiClient(session).bigPlan.loadBigPlan({
      ref_id: { the_id: id },
      allow_archived: true,
    });

    return json({
      bigPlan: result.big_plan,
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
        await getLoggedInApiClient(session).bigPlan.updateBigPlan({
          ref_id: { the_id: id },
          name: {
            should_change: true,
            value: { the_name: form.name },
          },
          status: {
            should_change: true,
            value: form.status,
          },
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

        return redirect(`/workspace/big-plans/${id}`);
      }

      case "change-project": {
        await getLoggedInApiClient(session).bigPlan.changeBigPlanProject({
          ref_id: { the_id: id },
          project_ref_id: { the_id: form.project },
        });

        return redirect(`/workspace/big-plans/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).bigPlan.archiveBigPlan({
          ref_id: { the_id: id },
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

export default function BigPlan() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.bigPlan.archived;

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
      key={loaderData.bigPlan.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={"/workspace/big-plans"}
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
                defaultValue={loaderData.bigPlan.name.the_name}
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

      <EntityActionHeader>
        <Button
          variant="contained"
          disabled={loaderData.bigPlan.archived}
          to={`/workspace/inbox-tasks/new?reason=for-big-plan&bigPlanRefId=${loaderData.bigPlan.ref_id.the_id}`}
          component={Link}
        >
          New Task
        </Button>
      </EntityActionHeader>

      {sortedInboxTasks.length > 0 && (
        <InboxTaskStack
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
    </LeafCard>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find big plan #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading big plan #${useParams().id}! Please try again!`
);
