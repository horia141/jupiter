import { ApiError, SyncTarget, WorkspaceFeature } from "@jupiter/webapi-client";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Autocomplete,
  Box,
  FormControl,
  InputLabel,
  Stack,
  TextField,
  styled,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntitySummaryLink } from "~/components/infra/entity-summary-link";
import { EventSourceTag } from "~/components/infra/event-source-tag";
import { EntityCard } from "~/components/infra/entity-card";
import { makeToolErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { StandardDivider } from "~/components/infra/standard-divider";
import { SyncTargetSelect } from "~/components/domain/core/sync-target-select";
import { SyncTargetTag } from "~/components/domain/core/sync-target-tag";
import { TimeDiffTag } from "~/components/domain/core/time-diff-tag";
import {
  fixSelectOutputEntityId,
  fixSelectOutputToEnum,
  selectZod,
} from "~/logic/select";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import {
  validationErrorToUIErrorInfo,
  noErrorNoData,
} from "~/logic/action-result";
import { SectionCard } from "~/components/infra/section-card";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";

interface HabitOptions {
  refId: string;
  label: string;
}

interface BigPlanOptions {
  refId: string;
  label: string;
}

interface JournalOptions {
  refId: string;
  label: string;
}

const StatsFormSchema = z.object({
  today: z.optional(z.string()),
  statsTargets: selectZod(z.nativeEnum(SyncTarget)),
  filterHabitRefIds: selectZod(z.string()),
  filterBigPlanRefIds: selectZod(z.string()),
  filterJournalRefIds: selectZod(z.string()),
});

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summariesResponse = await apiClient.getSummaries.getSummaries({
    include_big_plans: true,
    include_habits: true,
    include_journals_last_year: true,
  });
  const response = await apiClient.stats.statsLoadRuns({});
  return json({
    summaries: summariesResponse,
    loadRuns: response.entries,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, StatsFormSchema);

  try {
    await apiClient.stats.statsDo({
      stats_targets: fixSelectOutputToEnum<SyncTarget>(form.statsTargets),
      today: form.today,
      filter_habit_ref_ids: fixSelectOutputEntityId(form.filterHabitRefIds),
      filter_big_plan_ref_ids: fixSelectOutputEntityId(
        form.filterBigPlanRefIds,
      ),
      filter_journal_ref_ids: fixSelectOutputEntityId(form.filterJournalRefIds),
    });

    return json(noErrorNoData());
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

export default function Stats() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  const [selectedHabits, setSelectedHabits] = useState<HabitOptions[]>([]);
  const habitOptions =
    loaderData.summaries.habits?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  const [selectedBigPlans, setSelectedBigPlans] = useState<BigPlanOptions[]>(
    [],
  );
  const bigPlanOptions =
    loaderData.summaries.big_plans?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  const [selectedJournals, setSelectedJournals] = useState<JournalOptions[]>(
    [],
  );
  const journalOptions =
    loaderData.summaries.journals_last_year?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  return (
    <ToolPanel>
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="Stats"
        actions={
          <SectionActions
            id="stats-actions"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Compute Stats",
                value: "update",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <FormControl fullWidth>
          <InputLabel id="statsTargets">Stats Targets</InputLabel>
          <SyncTargetSelect
            topLevelInfo={topLevelInfo}
            labelId="statsTargets"
            label="Stats Targets"
            name="statsTargets"
            readOnly={!inputsEnabled}
          />
          <FieldError actionResult={actionData} fieldName="/stats_targets" />
        </FormControl>

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <AccordionHeader>Advanced Options & Filtering</AccordionHeader>
          </AccordionSummary>

          <AccordionDetails>
            <Stack spacing={2} useFlexGap>
              {isWorkspaceFeatureAvailable(
                topLevelInfo.workspace,
                WorkspaceFeature.HABITS,
              ) && (
                <FormControl fullWidth>
                  <Autocomplete
                    disablePortal
                    id="filterHabitRefIds"
                    options={habitOptions}
                    readOnly={!inputsEnabled}
                    disabled={!inputsEnabled}
                    multiple
                    onChange={(e, vol) => setSelectedHabits(vol)}
                    isOptionEqualToValue={(o, v) => o.refId === v.refId}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        name="filterHabitRefIds"
                        label="Generate Only For Habits"
                      />
                    )}
                  />
                  <input
                    type="hidden"
                    name="filterHabitRefIds"
                    value={selectedHabits.map((p) => p.refId).join(",")}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/filter_habit_ref_ids"
                  />
                </FormControl>
              )}

              {isWorkspaceFeatureAvailable(
                topLevelInfo.workspace,
                WorkspaceFeature.BIG_PLANS,
              ) && (
                <FormControl fullWidth>
                  <Autocomplete
                    disablePortal
                    id="filterBigPlanRefIds"
                    options={bigPlanOptions}
                    readOnly={!inputsEnabled}
                    disabled={!inputsEnabled}
                    multiple
                    onChange={(e, vol) => setSelectedBigPlans(vol)}
                    isOptionEqualToValue={(o, v) => o.refId === v.refId}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        name="filterBigPlanRefIds"
                        label="Generate Only For Big Plans"
                      />
                    )}
                  />
                  <input
                    type="hidden"
                    name="filterBigPlanRefIds"
                    value={selectedBigPlans.map((p) => p.refId).join(",")}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/filter_big_plan_ref_ids"
                  />
                </FormControl>
              )}

              {isWorkspaceFeatureAvailable(
                topLevelInfo.workspace,
                WorkspaceFeature.JOURNALS,
              ) && (
                <FormControl fullWidth>
                  <Autocomplete
                    disablePortal
                    id="filterJournalRefIds"
                    options={journalOptions}
                    readOnly={!inputsEnabled}
                    disabled={!inputsEnabled}
                    multiple
                    onChange={(e, vol) => setSelectedJournals(vol)}
                    isOptionEqualToValue={(o, v) => o.refId === v.refId}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        name="filterJournalRefIds"
                        label="Generate Only For Journals"
                      />
                    )}
                  />
                  <input
                    type="hidden"
                    name="filterJournalRefIds"
                    value={selectedJournals.map((p) => p.refId).join(",")}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/filter_journal_ref_ids"
                  />
                </FormControl>
              )}
            </Stack>
          </AccordionDetails>
        </Accordion>
      </SectionCard>

      <StandardDivider title="Stats Computation" size="large" />

      {loaderData.loadRuns.map((entry) => {
        return (
          <Accordion key={entry.ref_id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <AccordionHeader>
                Run from <EventSourceTag source={entry.source} />
                with {entry.entity_records.length} entities updated
                <TimeDiffTag
                  today={topLevelInfo.today}
                  labelPrefix="from"
                  collectionTime={entry.created_time}
                />
              </AccordionHeader>
            </AccordionSummary>

            <AccordionDetails>
              <StatsTargetsSection>
                Stats Targets:
                {entry.stats_targets.map((target) => (
                  <SyncTargetTag key={target} target={target} />
                ))}
              </StatsTargetsSection>

              {entry.entity_records.map((record) => (
                <EntityCard key={record.ref_id}>
                  <EntitySummaryLink
                    today={topLevelInfo.today}
                    summary={record}
                  />
                </EntityCard>
              ))}
            </AccordionDetails>
          </Accordion>
        );
      })}
    </ToolPanel>
  );
}

export const ErrorBoundary = makeToolErrorBoundary(
  () => `There was an error computing stats! Please try again!`,
);

const AccordionHeader = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
}));

const StatsTargetsSection = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
  paddingBottom: theme.spacing(1),
}));
