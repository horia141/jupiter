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
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { inboxTaskStatusName } from "~/logic/domain/inbox-task-status";
import { getIntent } from "~/logic/intent";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  fromAddress: z.string(),
  fromName: z.string(),
  toAddress: z.string(),
  subject: z.string(),
  body: z.string(),
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

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).emailTask.loadEmailTask({
      ref_id: { the_id: id },
      allow_archived: true,
    });

    return json({
      emailTask: response.email_task,
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
        await getLoggedInApiClient(session).emailTask.updateEmailTask({
          ref_id: { the_id: id },
          from_address: {
            should_change: true,
            value: { the_address: form.fromAddress },
          },
          from_name: {
            should_change: true,
            value: { the_name: form.fromName },
          },
          to_address: {
            should_change: true,
            value: { the_address: form.toAddress },
          },
          subject: {
            should_change: true,
            value: form.subject,
          },
          body: {
            should_change: true,
            value: form.body,
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

        return redirect(`/workspace/push-integrations/email-tasks/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).emailTask.archiveEmailTask({
          ref_id: { the_id: id },
        });

        return redirect(`/workspace/push-integrations/email-tasks/${id}`);
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

export default function EmailTask() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.emailTask.archived;

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
    <LeafCard
      key={loaderData.emailTask.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/push-integrations/email-tasks"
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="fromAddress">From Address</InputLabel>
              <OutlinedInput
                label="From Address"
                name="fromAddress"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.emailTask.from_address.the_address}
              />
              <FieldError actionResult={actionData} fieldName="/from_address" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="fromName">From Name</InputLabel>
              <OutlinedInput
                label="From Name"
                name="fromName"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.emailTask.from_name.the_name}
              />
              <FieldError actionResult={actionData} fieldName="/from_name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="toAddress">To Address</InputLabel>
              <OutlinedInput
                label="To Address"
                name="toAddress"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.emailTask.to_address.the_address}
              />
              <FieldError actionResult={actionData} fieldName="/to_address" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="subject">Subject</InputLabel>
              <OutlinedInput
                label="Subject"
                name="subject"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.emailTask.subject}
              />
              <FieldError actionResult={actionData} fieldName="/subject" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="body">Body</InputLabel>
              <OutlinedInput
                multiline
                minRows={2}
                maxRows={4}
                label="Body"
                name="body"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.emailTask.body}
              />
              <FieldError actionResult={actionData} fieldName="/body" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="generationName">Generation Name</InputLabel>
              <OutlinedInput
                label="Generation Name"
                name="generationName"
                readOnly={!inputsEnabled}
                defaultValue={
                  loaderData.emailTask.generation_extra_info?.name?.the_name
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
                  loaderData.emailTask.generation_extra_info?.status ||
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
                  loaderData.emailTask.generation_extra_info?.eisen || "default"
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
                  loaderData.emailTask.generation_extra_info?.difficulty ||
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
                  loaderData.emailTask.generation_extra_info?.actionable_date
                    ? aDateToDate(
                        loaderData.emailTask.generation_extra_info
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
                  loaderData.emailTask.generation_extra_info?.due_date
                    ? aDateToDate(
                        loaderData.emailTask.generation_extra_info?.due_date
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
    </LeafCard>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find email task #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading email task #${
      useParams().id
    }! Please try again!`
);
