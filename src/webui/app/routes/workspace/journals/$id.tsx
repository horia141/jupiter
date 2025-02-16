import type { InboxTask, ProjectSummary } from "@jupiter/webapi-client";
import {
  ApiError,
  InboxTaskStatus,
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
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { InboxTaskStack } from "~/components/inbox-task-stack";

import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { JournalStack } from "~/components/journal-stack";
import { ShowReport } from "~/components/show-report";
import { TimePlanStack } from "~/components/time-plan-stack";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { sortJournalsNaturally } from "~/logic/domain/journal";
import { periodName } from "~/logic/domain/period";
import { sortTimePlansNaturally } from "~/logic/domain/time-plan";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

import { makeLeafCatchBoundary } from "~/components/infra/catch-boundary";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("change-time-config"),
    rightNow: z.string(),
    period: z.nativeEnum(RecurringTaskPeriod),
  }),
  z.object({
    intent: z.literal("update-report"),
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

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_workspace: true,
    include_projects: true,
  });

  try {
    const workspace = summaryResponse.workspace!;

    const result = await apiClient.journals.journalLoad({
      ref_id: id,
      allow_archived: true,
    });

    let timePlanResult = undefined;
    if (isWorkspaceFeatureAvailable(workspace, WorkspaceFeature.TIME_PLANS)) {
      timePlanResult =
        await apiClient.timePlans.timePlanLoadForTimeDateAndPeriod({
          right_now: result.journal.right_now,
          period: result.journal.period,
          allow_archived: false,
        });
    }

    return json({
      allProjects: summaryResponse.projects as Array<ProjectSummary>,
      journal: result.journal,
      note: result.note,
      writingTask: result.writing_task,
      subPeriodJournals: result.sub_period_journals,
      timePlan: timePlanResult?.time_plan,
      subTimePlans: timePlanResult?.sub_period_time_plans ?? [],
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
      case "change-time-config": {
        await apiClient.journals.journalChangeTimeConfig({
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
        await apiClient.journals.journalUpdateReport({
          ref_id: id,
        });
        return redirect(`/workspace/journals/${id}`);
      }

      case "archive": {
        await apiClient.journals.journalArchive({
          ref_id: id,
        });
        return redirect(`/workspace/journals/${id}`);
      }

      case "remove": {
        await apiClient.journals.journalRemove({
          ref_id: id,
        });
        return redirect(`/workspace/journals`);
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

  const sortedSubJournals = sortJournalsNaturally(loaderData.subPeriodJournals);
  const sortedTimePlans = sortTimePlansNaturally(loaderData.subTimePlans);

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`journal-${loaderData.journal.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.journal.archived}
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
                notched
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
          today={today}
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

      <SectionCardNew id="sub-journals" title="Other Journals in this Period">
        <JournalStack
          topLevelInfo={topLevelInfo}
          journals={sortedSubJournals}
        />
      </SectionCardNew>

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.TIME_PLANS
      ) &&
        loaderData.timePlan &&
        sortedTimePlans.length > 0 && (
          <SectionCardNew id="sub-time-plans" title="Time Plans in this Period">
            {loaderData.timePlan && (
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={[loaderData.timePlan]}
              />
            )}
            {sortedTimePlans.length > 0 && (
              <TimePlanStack
                topLevelInfo={topLevelInfo}
                timePlans={sortedTimePlans}
              />
            )}
          </SectionCardNew>
        )}
    </LeafPanel>
  );
}

export const CatchBoundary = makeLeafCatchBoundary(
  `/workspace/journals`,
  () => `Could not find journal #${useParams().id}!`
);

export const ErrorBoundary = makeLeafErrorBoundary(
  "/workspace/journals",
  () =>
    `There was an error loading journal #${useParams().id}. Please try again!`
);
