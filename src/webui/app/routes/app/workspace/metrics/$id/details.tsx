import type { InboxTask } from "@jupiter/webapi-client";
import {
  ApiError,
  Difficulty,
  Eisen,
  InboxTaskStatus,
  NoteDomain,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";

import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useFetcher,
  useParams,
  useNavigation,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { IconSelector } from "~/components/icon-selector";
import { InboxTaskStack } from "~/components/inbox-task-stack";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";

import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { RecurringTaskGenParamsBlock } from "~/components/recurring-task-gen-params-block";
import { StandardDivider } from "~/components/standard-divider";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { sortInboxTasksNaturally } from "~/logic/domain/inbox-task";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const QuerySchema = {
  collectionTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    icon: z.string().optional(),
    collectionPeriod: z
      .union([z.nativeEnum(RecurringTaskPeriod), z.literal("none")])
      .optional(),
    collectionEisen: z.nativeEnum(Eisen).optional(),
    collectionDifficulty: z.nativeEnum(Difficulty).optional(),
    collectionActionableFromDay: z.string().optional(),
    collectionActionableFromMonth: z.string().optional(),
    collectionDueAtDay: z.string().optional(),
    collectionDueAtMonth: z.string().optional(),
  }),
  z.object({
    intent: z.literal("regen"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const query = parseQuery(request, QuerySchema);

  try {
    const response = await apiClient.metrics.metricLoad({
      ref_id: id,
      allow_archived: true,
      allow_archived_entries: false,
      collection_task_retrieve_offset: query.collectionTasksRetrieveOffset,
    });

    return json({
      metric: response.metric,
      note: response.note,
      collectionTasks: response.collection_tasks,
      collectionTasksTotalCnt: response.collection_tasks_total_cnt,
      collectionTasksPageSize: response.collection_tasks_page_size,
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
                : (form.collectionEisen as Eisen),
          },
          collection_difficulty: {
            should_change: true,
            value:
              form.collectionPeriod === "none"
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

        return redirect(`/app/workspace/metrics/${id}`);
      }

      case "regen": {
        await apiClient.metrics.metricRegen({
          ref_id: id,
        });

        return redirect(`/app/workspace/metrics/${id}/details`);
      }

      case "archive": {
        await apiClient.metrics.metricArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/metrics/${id}`);
      }

      case "remove": {
        await apiClient.metrics.metricRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/metrics`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.METRIC,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/metrics/${id}/archive`);
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
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.metric.archived;

  const sortedCollectionTasks = loaderData.collectionTasks
    ? sortInboxTasksNaturally(loaderData.collectionTasks, {
        dueDateAscending: false,
      })
    : undefined;

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

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`metric-${id}/details`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.metric.archived}
      returnLocation={`/app/workspace/metrics/${id}`}
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

            <StandardDivider title="Collection" size="large" />

            <RecurringTaskGenParamsBlock
              namePrefix="collection"
              fieldsPrefix="collection"
              allowNonePeriod
              period={loaderData.metric.collection_params?.period || "none"}
              eisen={loaderData.metric.collection_params?.eisen}
              difficulty={loaderData.metric.collection_params?.difficulty}
              actionableFromDay={
                loaderData.metric.collection_params?.actionable_from_day
              }
              actionableFromMonth={
                loaderData.metric.collection_params?.actionable_from_month
              }
              dueAtDay={loaderData.metric.collection_params?.due_at_day}
              dueAtMonth={loaderData.metric.collection_params?.due_at_month}
              inputsEnabled={inputsEnabled}
              actionData={actionData}
            />
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

      {sortedCollectionTasks && (
        <InboxTaskStack
          today={today}
          topLevelInfo={topLevelInfo}
          showOptions={{
            showStatus: true,
            showDueDate: true,
            showHandleMarkDone: true,
            showHandleMarkNotDone: true,
          }}
          label="Collection Tasks"
          inboxTasks={sortedCollectionTasks}
          withPages={{
            retrieveOffsetParamName: "collectionTasksRetrieveOffset",
            totalCnt: loaderData.collectionTasksTotalCnt,
            pageSize: loaderData.collectionTasksPageSize,
          }}
          onCardMarkDone={handleCardMarkDone}
          onCardMarkNotDone={handleCardMarkNotDone}
        />
      )}
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  () => `/app/workspace/metrics/${useParams().id}`,
  {
    notFound: () => `Could not find metric details for #${useParams().id}!`,
    error: () =>
      `There was an error loading metric details for #${useParams().id}! Please try again!`,
  },
);
