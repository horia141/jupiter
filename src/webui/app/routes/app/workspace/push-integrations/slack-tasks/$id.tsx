import type { InboxTask } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskStatus,
} from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormLabel,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useFetcher,
  useNavigation,
  useParams,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultySelect } from "~/components/difficulty-select";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { difficultyName } from "~/logic/domain/difficulty";
import { inboxTaskStatusName } from "~/logic/domain/inbox-task-status";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};
const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    user: z.string(),
    channel: z.string(),
    message: z.string(),
    generationName: z.string().optional(),
    generationStatus: z.nativeEnum(InboxTaskStatus).optional(),
    generationEisen: z.nativeEnum(Eisen),
    generationDifficulty: z.nativeEnum(Difficulty),
    generationActionableDate: z.string().optional(),
    generationDueDate: z.string().optional(),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await apiClient.slack.slackTaskLoad({
      ref_id: id,
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.slack.slackTaskUpdate({
          ref_id: id,
          user: {
            should_change: true,
            value: form.user,
          },
          channel: {
            should_change: true,
            value: form.channel,
          },
          message: {
            should_change: true,
            value: form.message,
          },
          generation_name: {
            should_change: true,
            value: form.generationName,
          },
          generation_status: {
            should_change: true,
            value: form.generationStatus,
          },
          generation_eisen: {
            should_change: true,
            value: form.generationEisen,
          },
          generation_difficulty: {
            should_change: true,
            value: form.generationDifficulty,
          },
          generation_actionable_date: {
            should_change: true,
            value:
              form.generationActionableDate !== undefined &&
              form.generationActionableDate !== ""
                ? form.generationActionableDate
                : undefined,
          },
          generation_due_date: {
            should_change: true,
            value:
              form.generationDueDate !== undefined &&
              form.generationDueDate !== ""
                ? form.generationDueDate
                : undefined,
          },
        });

        return redirect(`/app/workspace/push-integrations/slack-tasks`);
      }

      case "archive": {
        await apiClient.slack.slackTaskArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/push-integrations/slack-tasks`);
      }

      case "remove": {
        await apiClient.slack.slackTaskRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/push-integrations/slack-tasks`);
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
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.slackTask.archived;

  const cardActionFetcher = useFetcher();

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

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

  return (
    <LeafPanel
      key={`slack-tasks/${loaderData.slackTask.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.slackTask.archived}
      returnLocation="/app/workspace/push-integrations/slack-tasks"
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
                defaultValue={loaderData.slackTask.user}
              />
              <FieldError actionResult={actionData} fieldName="/user" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="channel">Channel</InputLabel>
              <OutlinedInput
                label="Channel"
                name="channel"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.slackTask.channel}
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
                defaultValue={loaderData.slackTask.generation_extra_info?.name}
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
                  InboxTaskStatus.NOT_STARTED
                }
                label="Status"
              >
                {Object.values(InboxTaskStatus)
                  .filter((s) => {
                    return s !== InboxTaskStatus.NOT_STARTED_GEN;
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
              <FormLabel id="generationEisen">Generation Eisenhower</FormLabel>
              <EisenhowerSelect
                name="generationEisen"
                inputsEnabled={inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.eisen ||
                  Eisen.REGULAR
                }
              />
              <FieldError
                actionResult={actionData}
                fieldName="/generation_eisen"
              />
            </FormControl>

            <FormControl fullWidth>
              <FormLabel id="generationDifficulty">
                Generation Difficulty
              </FormLabel>
              <DifficultySelect
                name="generationDifficulty"
                inputsEnabled={inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.difficulty ||
                  Difficulty.EASY
                }
              />
              <FieldError
                actionResult={actionData}
                fieldName="/generation_difficulty"
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
              <InputLabel id="generationActionableDate" shrink>
                Generation Actionable From
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="generationActionableDate"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.actionable_date
                    ? aDateToDate(
                        loaderData.slackTask.generation_extra_info
                          ?.actionable_date,
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
              <InputLabel id="generationDueDate" shrink>
                Generation Due At
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="generationDueDate"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.slackTask.generation_extra_info?.due_date
                    ? aDateToDate(
                        loaderData.slackTask.generation_extra_info?.due_date,
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
          today={today}
          topLevelInfo={topLevelInfo}
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

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/push-integrations/slack-tasks",
  {
    notFound: () => `Could not find slack task #${useParams().id}!`,
    error: () =>
      `There was an error loading slack task #${useParams().id}! Please try again!`,
  },
);
