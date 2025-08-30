import type { InboxTask } from "@jupiter/webapi-client";
import {
  ApiError,
  InboxTaskStatus,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import {
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useFetcher, useNavigation } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/infra/entity-note-editor";
import { InboxTaskStack } from "~/components/domain/concept/inbox-task/inbox-task-stack";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { periodName } from "~/logic/domain/period";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { SectionCard } from "~/components/infra/section-card";
import { GlobalError } from "~/components/infra/errors";

const ParamsSchema = z.object({
  id: z.string(),
});

const QuerySchema = z.object({
  cleanupTasksRetrieveOffset: z
    .string()
    .transform((s) => parseInt(s, 10))
    .optional(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({ intent: z.literal("archive") }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const query = parseQuery(request, QuerySchema);

  try {
    const result = await apiClient.workingMem.workingMemLoad({
      ref_id: id,
      allow_archived: true,
      cleanup_task_retrieve_offset: query.cleanupTasksRetrieveOffset,
    });

    return json({
      workingMem: result.working_mem,
      note: result.note,
      cleanupTasks: result.cleanup_tasks,
      cleanupTasksTotalCnt: result.cleanup_tasks_total_cnt,
      cleanupTasksPageSize: result.cleanup_tasks_page_size,
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
      case "archive": {
        await apiClient.workingMem.workingMemArchive({
          ref_id: id,
        });
        return redirect(`/app/workspace/working-mem/archive/${id}`);
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

export default function WorkingMem() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const inputsEnabled =
    navigation.state === "idle" && !loaderData.workingMem.archived;

  const topLevelInfo = useContext(TopLevelInfoContext);

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

  return (
    <LeafPanel
      key={`working-mem-${loaderData.workingMem.ref_id}`}
      fakeKey={`working-mem-${loaderData.workingMem.ref_id}`}
      showArchiveAndRemoveButton={
        aDateToDate(loaderData.workingMem.right_now) <
        aDateToDate(topLevelInfo.today).minus({ days: 14 })
      }
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.workingMem.archived}
      returnLocation="/app/workspace/working-mem/archive"
    >
      <GlobalError actionResult={actionData} />
      <SectionCard title="Properties">
        <Stack direction={"row"} spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="rightNow" shrink margin="dense">
              The Date
            </InputLabel>
            <OutlinedInput
              type="date"
              notched
              label="rightNow"
              name="rightNow"
              readOnly={true}
              defaultValue={loaderData.workingMem.right_now}
            />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="period">Period</InputLabel>
            <Select
              labelId="status"
              name="period"
              readOnly={true}
              defaultValue={loaderData.workingMem.period}
              label="Period"
            >
              {Object.values(RecurringTaskPeriod).map((s) => (
                <MenuItem key={s} value={s}>
                  {periodName(s)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </SectionCard>

      <SectionCard title="Content">
        <EntityNoteEditor
          initialNote={loaderData.note}
          inputsEnabled={inputsEnabled}
        />
      </SectionCard>

      <SectionCard title="Cleanup Tasks">
        {loaderData.cleanupTasks.length > 0 && (
          <InboxTaskStack
            topLevelInfo={topLevelInfo}
            showOptions={{
              showStatus: true,
              showDueDate: true,
              showHandleMarkDone: true,
              showHandleMarkNotDone: true,
            }}
            inboxTasks={loaderData.cleanupTasks}
            withPages={{
              retrieveOffsetParamName: "cleanupTasksRetrieveOffset",
              totalCnt: loaderData.cleanupTasksTotalCnt,
              pageSize: loaderData.cleanupTasksPageSize,
            }}
            onCardMarkDone={handleCardMarkDone}
            onCardMarkNotDone={handleCardMarkNotDone}
          />
        )}
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/working-mem",
  ParamsSchema,
  {
    notFound: (params) => `Could not find archived item with ID ${params.id}!`,
    error: (params) =>
      `There was an error loading archived item with ID ${params.id}! Please try again!`,
  },
);
