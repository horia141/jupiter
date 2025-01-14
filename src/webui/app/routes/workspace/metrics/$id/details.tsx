import type { InboxTask } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  NoteDomain,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import type { SelectChangeEvent } from "@mui/material";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  Divider,
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
  useActionData,
  useFetcher,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { IconSelector } from "~/components/icon-selector";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { periodName } from "~/logic/domain/period";
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
  name: z.string(),
  icon: z.string().optional(),
  collectionPeriod: z
    .union([z.nativeEnum(RecurringTaskPeriod), z.literal("none")])
    .optional(),
  collectionEisen: z
    .union([z.nativeEnum(Eisen), z.literal("default")])
    .optional(),
  collectionDifficulty: z
    .union([z.nativeEnum(Difficulty), z.literal("default")])
    .optional(),
  collectionActionableFromDay: z.string().optional(),
  collectionActionableFromMonth: z.string().optional(),
  collectionDueAtDay: z.string().optional(),
  collectionDueAtMonth: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await apiClient.metrics.metricLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      metric: response.metric,
      note: response.note,
      collectionInboxTasks: response.metric_collection_inbox_tasks,
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
        await apiClient.metrics.metricUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          icon: {
            should_change: true,
            value: form.icon,
          },
          collection_period: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : (form.collectionPeriod as RecurringTaskPeriod),
          },
          collection_eisen: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : form.collectionEisen === "default"
                ? undefined
                : (form.collectionEisen as Eisen),
          },
          collection_difficulty: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : form.collectionDifficulty === "default"
                ? undefined
                : (form.collectionDifficulty as Difficulty),
          },
          collection_actionable_from_day: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : form.collectionActionableFromDay === undefined ||
                  form.collectionActionableFromDay === ""
                ? undefined
                : parseInt(form.collectionActionableFromDay),
          },
          collection_actionable_from_month: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : form.collectionActionableFromMonth === undefined ||
                  form.collectionActionableFromMonth === ""
                ? undefined
                : parseInt(form.collectionActionableFromMonth),
          },
          collection_due_at_day: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : form.collectionDueAtDay === undefined ||
                  form.collectionDueAtDay === ""
                ? undefined
                : parseInt(form.collectionDueAtDay),
          },
          collection_due_at_month: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
                ? undefined
                : form.collectionDueAtMonth === undefined ||
                  form.collectionDueAtMonth === ""
                ? undefined
                : parseInt(form.collectionDueAtMonth),
          },
        });

        return redirect(`/workspace/metrics/${id}/details`);
      }

      case "archive": {
        await apiClient.metrics.metricArchive({
          ref_id: id,
        });

        return redirect(`/workspace/metrics/${id}/details`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.METRIC,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/workspace/metrics/${id}/details`);
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

export default function MetricDetails() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    transition.state === "idle" && !loaderData.metric.archived;

  const [showCollectionParams, setShowCollectionParams] = useState(
    loaderData.metric.collection_params !== undefined
  );

  const sortedCollectionTasks = loaderData.collectionInboxTasks
    ? sortInboxTasksNaturally(loaderData.collectionInboxTasks, {
        dueDateAscending: false,
      })
    : undefined;

  useEffect(() => {
    setShowCollectionParams(loaderData.metric.collection_params !== undefined);
  }, [loaderData]);

  function handleChangeCollectionPeriod(event: SelectChangeEvent) {
    if (event.target.value === "none") {
      setShowCollectionParams(false);
    } else {
      setShowCollectionParams(true);
    }
  }

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

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`metric-${id}/details`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/metrics/${id}`}
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
                defaultValue={loaderData.metric.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="icon">Icon</InputLabel>
              <IconSelector
                readOnly={!inputsEnabled}
                defaultIcon={loaderData.metric.icon}
              />
              <FieldError actionResult={actionData} fieldName="/icon" />
            </FormControl>

            <Divider>Collection</Divider>

            <FormControl fullWidth>
              <InputLabel id="collectionPeriod">Collection Period</InputLabel>
              <Select
                labelId="collectionPeriod"
                name="collectionPeriod"
                readOnly={!inputsEnabled}
                onChange={handleChangeCollectionPeriod}
                defaultValue={
                  loaderData.metric.collection_params?.period || "none"
                }
                label="Collection Period"
              >
                <MenuItem value={"none"}>None</MenuItem>
                {Object.values(RecurringTaskPeriod).map((period) => (
                  <MenuItem key={period} value={period}>
                    {periodName(period)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/collection_period"
              />
            </FormControl>

            {showCollectionParams && (
              <>
                <FormControl fullWidth>
                  <InputLabel id="collectionEisen">Eisenhower</InputLabel>
                  <Select
                    labelId="collectionEisen"
                    name="collectionEisen"
                    readOnly={!inputsEnabled}
                    defaultValue={
                      loaderData.metric.collection_params?.eisen || "default"
                    }
                    label="Eisenhower"
                  >
                    <MenuItem value="default">Default</MenuItem>
                    {Object.values(Eisen).map((e) => (
                      <MenuItem key={e} value={e}>
                        {eisenName(e)}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_eisen"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionDifficulty">Difficulty</InputLabel>
                  <Select
                    labelId="collectionDifficulty"
                    name="collectionDifficulty"
                    readOnly={!inputsEnabled}
                    defaultValue={
                      loaderData.metric.collection_params?.difficulty ||
                      "default"
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
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_difficulty"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionActionableFromDay">
                    Actionable From Day
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Actionable From Day"
                    name="collectionActionableFromDay"
                    readOnly={!inputsEnabled}
                    defaultValue={
                      loaderData.metric.collection_params
                        ?.actionable_from_day || ""
                    }
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_actionable_from_day"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionActionableFromMonth">
                    Actionable From Month
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Actionable From Month"
                    name="collectionActionableFromMonth"
                    readOnly={!inputsEnabled}
                    defaultValue={
                      loaderData.metric.collection_params
                        ?.actionable_from_month || ""
                    }
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_actionable_from_month"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionDueAtDay">Due At Day</InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Due At Day"
                    name="collectionDueAtDay"
                    readOnly={!inputsEnabled}
                    defaultValue={
                      loaderData.metric.collection_params?.due_at_day || ""
                    }
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_due_at_day"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionDueAtMonth">
                    Due At Month
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Due At Month"
                    name="collectionDueAtMonth"
                    readOnly={!inputsEnabled}
                    defaultValue={
                      loaderData.metric.collection_params?.due_at_month || ""
                    }
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_due_at_month"
                  />
                </FormControl>
              </>
            )}
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

      {sortedCollectionTasks && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
          showLabel
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Collection Tasks"
          inboxTasks={sortedCollectionTasks}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find metric #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading metric #${useParams().id}! Please try again!`
);
