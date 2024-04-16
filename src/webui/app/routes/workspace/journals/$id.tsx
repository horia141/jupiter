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
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { InboxTask, ProjectSummary } from "@jupiter/webapi-client";
import { ApiError, InboxTaskStatus, RecurringTaskPeriod } from "@jupiter/webapi-client";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ShowReport } from "~/components/show-report";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  rightNow: z.string(),
  period: z.nativeEnum(RecurringTaskPeriod),
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
    const result = await getLoggedInApiClient(session).journals.journalLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
      journal: result.journal,
      note: result.note,
      writingTask: result.writing_task,
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

  try {
    switch (form.intent) {
      case "change-time-config": {
        await getLoggedInApiClient(session).journals.journalChangeTimeConfig({
          ref_id: id,
          right_now: {
            should_change: true,
            value: form.rightNow,
          },
          period: {
            should_change: true,
            value: form.period,
          },
        });
        return redirect(`/workspace/journals/${id}`);
      }

      case "update-report": {
        await getLoggedInApiClient(session).journals.journalUpdateReport({
          ref_id: id,
        });
        return redirect(`/workspace/journals/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).journals.journalArchive({
          ref_id: id,
        });
        return redirect(`/workspace/journals/${id}`);
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

    if (error instanceof ApiError && error.status === StatusCodes.CONFLICT) {
      return json(aGlobalError(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Journal() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const isBigScreen = useBigScreen();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.journal.archived;

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

  return (
    <LeafPanel
      key={loaderData.journal.ref_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/journals"
      initialExpansionState={LeafPanelExpansionState.FULL}
    >
      <GlobalError actionResult={actionData} />
      <Card
        sx={{
          marginBottom: "1rem",
          display: "flex",
          flexDirection: isBigScreen ? "row" : "column",
        }}
      >
        <CardContent sx={{ flexGrow: "1" }}>
          <Stack direction={"row"} spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="rightNow" shrink margin="dense">
                The Date
              </InputLabel>
              <OutlinedInput
                type="date"
                label="rightNow"
                name="rightNow"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.journal.right_now}
              />

              <FieldError actionResult={actionData} fieldName="/right_now" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="period">Period</InputLabel>
              <Select
                labelId="status"
                name="period"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.journal.period}
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
          </Stack>
        </CardContent>
        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="change-time-config"
            >
              Save
            </Button>

            <Button
              variant="outlined"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update-report"
            >
              Update Report
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
      <Card>
        <CardContent>
          <EntityNoteEditor
            initialNote={loaderData.note}
            inputsEnabled={inputsEnabled}
          />
        </CardContent>
      </Card>

      <ShowReport
        topLevelInfo={topLevelInfo}
        allProjects={loaderData.allProjects}
        report={loaderData.journal.report}
      />

      {loaderData.writingTask && (
        <InboxTaskStack
          topLevelInfo={topLevelInfo}
          showLabel
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Writing Task"
          inboxTasks={[loaderData.writingTask]}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find journal #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading journal #${useParams().id}. Please try again!`
);
