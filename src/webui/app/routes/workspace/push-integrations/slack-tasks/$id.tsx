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
  ShouldRevalidateFunction,
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { InboxTask } from "jupiter-gen";
import { ApiError, Difficulty, Eisen, InboxTaskStatus } from "jupiter-gen";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { inboxTaskStatusName } from "~/logic/domain/inbox-task-status";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

const UpdateFormSchema = {
  intent: z.string(),
  user: z.string(),
  channel: z.string().optional(),
  message: z.string().optional(),
  generationName: z.string().optional(),
  generationStatus: z.nativeEnum(InboxTaskStatus).optional(),
  generationEisen: z
    .union([z.nativeEnum(Eisen), z.literal("default")])
    .optional(),
  generationDifficulty: z
    .union([z.nativeEnum(Difficulty), z.literal("default")])
    .optional(),
  generationActionableDate: z.string().optional(),
  generationDueDate: z.string().optional(),
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).pushIntegrations.slackTaskLoad({
      ref_id: { the_id: id },
      allow_archived: true,
    });

    return json({
      slackTask: response.slack_task,
      inboxTask: response.inbox_task,
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
        await getLoggedInApiClient(session).pushIntegrations.slackTaskUpdate({
          ref_id: { the_id: id },
          user: {
            should_change: true,
            value: { the_name: form.user },
          },
          channel: {
            should_change: true,
            value: form.channel ? { the_name: form.channel } : undefined,
          },
          message: {
            should_change: true,
            value: form.message,
          },
          generation_name: {
            should_change: true,
            value: form.generationName
              ? { the_name: form.generationName }
              : undefined,
          },
          generation_status: {
            should_change: true,
            value: form.generationStatus,
          },
          generation_eisen: {
            should_change: true,
            value:
              form.generationEisen && form.generationEisen !== "default"
                ? form.generationEisen
                : undefined,
          },
          generation_difficulty: {
            should_change: true,
            value:
              form.generationDifficulty &&
              form.generationDifficulty !== "default"
                ? form.generationDifficulty
                : undefined,
          },
          generation_actionable_date: {
            should_change: true,
            value:
              form.generationActionableDate !== undefined &&
              form.generationActionableDate !== ""
                ? {
                    the_date: form.generationActionableDate,
                    the_datetime: undefined,
                  }
                : undefined,
          },
          generation_due_date: {
            should_change: true,
            value:
              form.generationDueDate !== undefined &&
              form.generationDueDate !== ""
                ? { the_date: form.generationDueDate, the_datetime: undefined }
                : undefined,
          },
        });

        return redirect(`/workspace/push-integrations/slack-tasks/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).pushIntegrations.slackTaskArchive({
          ref_id: { the_id: id },
        });

        return redirect(`/workspace/push-integrations/slack-tasks/${id}`);
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

export default function SlackTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.slackTask.archived;

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

  return (
    <LeafPanel
      key={loaderData.slackTask.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/push-integrations/slack-tasks"
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="user">User</InputLabel>
              <OutlinedInput
                label="User"
                name="user"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.slackTask.user.the_name}
              />
              <FieldError actionResult={actionData} fieldName="/user" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="channel">Channel</InputLabel>
              <OutlinedInput
                label="Channel"
                name="channel"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.slackTask.channel?.the_name}
              />
              <FieldError actionResult={actionData} fieldName="/channel" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="message">Message</InputLabel>
              <OutlinedInput
                label="Message"
                name="message"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.slackTask.message}
              />
              <FieldError actionResult={actionData} fieldName="/message" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationName">Generation Name</InputLabel>
              <OutlinedInput
                label="Generation Name"
                name="generationName"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.name?.the_name
                }
              />
              <FieldError
                actionResult={actionData}
                fieldName="/generation_name"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationStatus">Generation Status</InputLabel>
              <Select
                labelId="generationStatus"
                name="generationStatus"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.status ||
                  InboxTaskStatus.ACCEPTED
                }
                label="Status"
              >
                {Object.values(InboxTaskStatus)
                  .filter((s) => {
                    return s !== InboxTaskStatus.RECURRING;
                  })
                  .map((s) => (
                    <MenuItem key={s} value={s}>
                      {inboxTaskStatusName(s)}
                    </MenuItem>
                  ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/generation_status"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationEisen">
                Generation Eisenhower
              </InputLabel>
              <Select
                labelId="generationEisen"
                name="generationEisen"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.eisen || "default"
                }
                label="Generation Eisenhower"
              >
                <MenuItem value={"default"}>Default</MenuItem>
                {Object.values(Eisen).map((e) => (
                  <MenuItem key={e} value={e}>
                    {eisenName(e)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/generation_eisen"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationDifficulty">
                Generation Difficulty
              </InputLabel>
              <Select
                labelId="generationDifficulty"
                name="generationDifficulty"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.difficulty ||
                  "default"
                }
                label="Generation Difficulty"
              >
                <MenuItem value="default">Default</MenuItem>
                {Object.values(Difficulty).map((e) => (
                  <MenuItem key={e} value={e}>
                    {difficultyName(e)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/generation_difficulty"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationActionableDate">
                Generation Actionable From
              </InputLabel>
              <OutlinedInput
                type="date"
                label="generationActionableDate"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.actionable_date
                    ? aDateToDate(
                        loaderData.slackTask.generation_extra_info
                          ?.actionable_date
                      ).toFormat("yyyy-MM-dd")
                    : undefined
                }
                name="generationActionableDate"
              />

              <FieldError
                actionResult={actionData}
                fieldName="/generation_actionable_date"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationDueDate">Generation Due At</InputLabel>
              <OutlinedInput
                type="date"
                label="generationDueDate"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.due_date
                    ? aDateToDate(
                        loaderData.slackTask.generation_extra_info?.due_date
                      ).toFormat("yyyy-MM-dd")
                    : undefined
                }
                name="generationDueDate"
              />
              <FieldError
                actionResult={actionData}
                fieldName="/generation_due_date"
              />
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
          </ButtonGroup>
        </CardActions>
      </Card>

      {loaderData.inboxTask && (
        <InboxTaskStack
          topLevelInfo={topLevelInfo}
          showLabel
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Inbox Task"
          inboxTasks={[loaderData.inboxTask]}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find Slack task #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading Slack task #${
      useParams().id
    }! Please try again!`
);
