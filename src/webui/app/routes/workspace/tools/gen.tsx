import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Autocomplete,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  styled,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import {
  ApiError,
  EventSource,
  RecurringTaskPeriod,
  SyncTarget,
  WorkspaceFeature,
} from "webapi-client";
import { DateTime } from "luxon";
import React, { useContext, useState } from "react";
import { z } from "zod";
import { CheckboxAsString, parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { ADateTag } from "~/components/adate-tag";
import { EntitySummaryLink } from "~/components/entity-summary-link";
import { EventSourceTag } from "~/components/event-source-tag";
import { SlimChip } from "~/components/infra/chips";
import { EntityCard } from "~/components/infra/entity-card";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { PeriodSelect } from "~/components/period-select";
import { PeriodTag } from "~/components/period-tag";
import { SyncTargetSelect } from "~/components/sync-target-select";
import { SyncTargetTag } from "~/components/sync-target-tag";
import { TimeDiffTag } from "~/components/time-diff-tag";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import {
  fixSelectOutputEntityId,
  fixSelectOutputToEnum,
  selectZod,
} from "~/logic/select";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

interface ProjectOption {
  refId: string;
  label: string;
}

interface HabitOptions {
  refId: string;
  label: string;
}

interface ChoreOptions {
  refId: string;
  label: string;
}

interface MetricOptions {
  refId: string;
  label: string;
}

interface PersonOptions {
  refId: string;
  label: string;
}

const GenFormSchema = {
  gen_even_if_not_modified: CheckboxAsString,
  today: z.optional(z.string()),
  gen_targets: selectZod(z.nativeEnum(SyncTarget)),
  period: selectZod(z.nativeEnum(RecurringTaskPeriod)),
  filter_project_ref_ids: selectZod(z.string()),
  filter_habit_ref_ids: selectZod(z.string()),
  filter_chore_ref_ids: selectZod(z.string()),
  filter_metric_ref_ids: selectZod(z.string()),
  filter_person_ref_ids: selectZod(z.string()),
};

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summariesResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
    include_habits: true,
    include_chores: true,
    include_metrics: true,
    include_persons: true,
  });
  const loadRunsResponse = await getLoggedInApiClient(session).gen.genLoadRuns(
    {}
  );

  return {
    summaries: summariesResponse,
    loadRuns: loadRunsResponse,
  };
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, GenFormSchema);

  try {
    await getLoggedInApiClient(session).gen.genDo({
      source: EventSource.WEB,
      gen_even_if_not_modified: form.gen_even_if_not_modified,
      today:
        form.today !== undefined && form.today !== ""
          ? DateTime.fromISO(form.today, {
              zone: "utc",
            }).toISODate()
          : undefined,
      gen_targets: fixSelectOutputToEnum<SyncTarget>(form.gen_targets),
      period: fixSelectOutputToEnum<RecurringTaskPeriod>(form.period),
      filter_project_ref_ids: fixSelectOutputEntityId(
        form.filter_project_ref_ids
      ),
      filter_habit_ref_ids: fixSelectOutputEntityId(form.filter_habit_ref_ids),
      filter_chore_ref_ids: fixSelectOutputEntityId(form.filter_chore_ref_ids),
      filter_metric_ref_ids: fixSelectOutputEntityId(
        form.filter_metric_ref_ids
      ),
      filter_person_ref_ids: fixSelectOutputEntityId(
        form.filter_person_ref_ids
      ),
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

export default function Gen() {
  const transition = useTransition();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  const [selectedProjects, setSelectedProjects] = useState<ProjectOption[]>([]);
  const projectOptions =
    loaderData.summaries.projects?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  const [selectedHabits, setSelectedHabits] = useState<HabitOptions[]>([]);
  const habitOptions =
    loaderData.summaries.habits?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  const [selectedChores, setSelectedChores] = useState<ChoreOptions[]>([]);
  const choreOptions =
    loaderData.summaries.chores?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  const [selectedMetrics, setSelectedMetrics] = useState<MetricOptions[]>([]);
  const metricOptions =
    loaderData.summaries.metrics?.map((p) => ({
      refId: p.ref_id,
      label: p.icon ? `${p.icon} ${p.name}` : p.name,
    })) ?? [];

  const [selectedPersons, setSelectedPersons] = useState<PersonOptions[]>([]);
  const personOptions =
    loaderData.summaries.persons?.map((p) => ({
      refId: p.ref_id,
      label: p.name,
    })) ?? [];

  return (
    <ToolPanel>
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <FormControlLabel
                control={
                  <Switch
                    name="gen_even_if_not_modified"
                    readOnly={!inputsEnabled}
                    disabled={!inputsEnabled}
                    defaultChecked={false}
                  />
                }
                label="Generate Even If Not Modified"
              />
              <FieldError
                actionResult={actionData}
                fieldName="/gen_even_if_not_modified"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="today">Generation Date</InputLabel>
              <OutlinedInput
                type="date"
                label="Generation Date"
                readOnly={!inputsEnabled}
                disabled={!inputsEnabled}
                defaultValue={DateTime.now().toISODate()}
                name="today"
              />

              <FieldError actionResult={actionData} fieldName="/today" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="gen_targets">Generation Targets</InputLabel>
              <SyncTargetSelect
                topLevelInfo={topLevelInfo}
                labelId="gen_targets"
                label="Generation Targets"
                name="gen_targets"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/gen_targets" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="period">Generation Period</InputLabel>
              <PeriodSelect
                labelId="period"
                label="Generation Period"
                name="period"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/period" />
            </FormControl>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="filter_project_ref_ids"
                  options={projectOptions}
                  readOnly={!inputsEnabled}
                  disabled={!inputsEnabled}
                  multiple
                  onChange={(e, vol) => setSelectedProjects(vol)}
                  isOptionEqualToValue={(o, v) => o.refId === v.refId}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      name="filter_project_ref_ids"
                      label="Generate Only For Projects"
                    />
                  )}
                />
                <input
                  type="hidden"
                  name="filter_project_ref_ids"
                  value={selectedProjects.map((p) => p.refId).join(",")}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/filter_project_ref_ids"
                />
              </FormControl>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.HABITS
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="filter_habit_ref_ids"
                  options={habitOptions}
                  readOnly={!inputsEnabled}
                  disabled={!inputsEnabled}
                  multiple
                  onChange={(e, vol) => setSelectedHabits(vol)}
                  isOptionEqualToValue={(o, v) => o.refId === v.refId}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      name="filter_habit_ref_ids"
                      label="Generate Only For Habits"
                    />
                  )}
                />
                <input
                  type="hidden"
                  name="filter_habit_ref_ids"
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
              WorkspaceFeature.CHORES
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="filter_chore_ref_ids"
                  options={choreOptions}
                  readOnly={!inputsEnabled}
                  disabled={!inputsEnabled}
                  multiple
                  onChange={(e, vol) => setSelectedChores(vol)}
                  isOptionEqualToValue={(o, v) => o.refId === v.refId}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      name="filter_chore_ref_ids"
                      label="Generate Only For Chores"
                    />
                  )}
                />
                <input
                  type="hidden"
                  name="filter_chore_ref_ids"
                  value={selectedChores.map((p) => p.refId).join(",")}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/filter_chore_ref_ids"
                />
              </FormControl>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.METRICS
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="filter_metric_ref_ids"
                  options={metricOptions}
                  readOnly={!inputsEnabled}
                  disabled={!inputsEnabled}
                  multiple
                  onChange={(e, vol) => setSelectedMetrics(vol)}
                  isOptionEqualToValue={(o, v) => o.refId === v.refId}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      name="filter_metric_ref_ids"
                      label="Generate Only For Metrics"
                    />
                  )}
                />
                <input
                  type="hidden"
                  name="filter_metric_ref_ids"
                  value={selectedMetrics.map((p) => p.refId).join(",")}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/filter_metric_ref_ids"
                />
              </FormControl>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PERSONS
            ) && (
              <FormControl fullWidth>
                <Autocomplete
                  disablePortal
                  id="filter_person_ref_ids"
                  options={personOptions}
                  disabled={!inputsEnabled}
                  readOnly={!inputsEnabled}
                  multiple
                  onChange={(e, vol) => setSelectedPersons(vol)}
                  isOptionEqualToValue={(o, v) => o.refId === v.refId}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      name="filter_person_ref_ids"
                      label="Generate Only For Persons"
                    />
                  )}
                />
                <input
                  type="hidden"
                  name="filter_person_ref_ids"
                  value={selectedPersons.map((p) => p.refId).join(",")}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/filter_person_ref_ids"
                />
              </FormControl>
            )}
          </Stack>
        </CardContent>

        <CardActions>
          <Button
            variant="contained"
            disabled={!inputsEnabled}
            type="submit"
            name="intent"
            value="update"
          >
            Generate
          </Button>
        </CardActions>
      </Card>

      <Divider style={{ paddingTop: "1rem", paddingBottom: "1rem" }}>
        <Typography variant="h6">Previous Runs</Typography>
      </Divider>

      {loaderData.loadRuns.entries.map((entry) => {
        return (
          <Accordion key={entry.ref_id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <AccordionHeader>
                Run from <EventSourceTag source={entry.source} />
                with {entry.entity_created_records.length} entities created,{" "}
                {entry.entity_updated_records.length} entities updated, and{" "}
                {entry.entity_removed_records.length} entities removed
                <TimeDiffTag
                  labelPrefix="from"
                  collectionTime={entry.created_time}
                />
              </AccordionHeader>
            </AccordionSummary>

            <AccordionDetails>
              <GenTargetsSection>
                Generate even if not modified:{" "}
                {entry.gen_even_if_not_modified ? "✅" : "⛔"}
              </GenTargetsSection>
              <GenTargetsSection>
                Generate for: <ADateTag date={entry.today} label={""} />
              </GenTargetsSection>
              <GenTargetsSection>
                Gen targets:
                {entry.gen_targets.map((target) => (
                  <SyncTargetTag key={target} target={target} />
                ))}
              </GenTargetsSection>
              <GenTargetsSection>
                Period:{" "}
                {entry.period &&
                  entry.period.map((p) => <PeriodTag key={p} period={p} />)}
                {!entry.period && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter projects ref ids:{" "}
                {entry.filter_project_ref_ids &&
                  entry.filter_project_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_project_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter habits ref ids:{" "}
                {entry.filter_habit_ref_ids &&
                  entry.filter_habit_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_habit_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter chores ref ids:{" "}
                {entry.filter_chore_ref_ids &&
                  entry.filter_chore_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_chore_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter metrics ref ids:{" "}
                {entry.filter_metric_ref_ids &&
                  entry.filter_metric_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_metric_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter persons ref ids:{" "}
                {entry.filter_person_ref_ids &&
                  entry.filter_person_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_person_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter Slack task ref ids:{" "}
                {entry.filter_slack_task_ref_ids &&
                  entry.filter_slack_task_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_slack_task_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>
              <GenTargetsSection>
                Filter email task ref ids:{" "}
                {entry.filter_email_task_ref_ids &&
                  entry.filter_email_task_ref_ids.map((refId) => (
                    <React.Fragment key={refId}>{refId}</React.Fragment>
                  ))}
                {!entry.filter_email_task_ref_ids && <SlimChip label={"All"} />}
              </GenTargetsSection>

              {entry.entity_created_records.length > 0 && (
                <>
                  <Divider
                    style={{ paddingTop: "1rem", paddingBottom: "1rem" }}
                  >
                    <Typography variant="h6">Created entities</Typography>
                  </Divider>

                  {entry.entity_created_records.map((record) => (
                    <EntityCard key={record.ref_id}>
                      <EntitySummaryLink summary={record} />
                    </EntityCard>
                  ))}
                </>
              )}

              {entry.entity_updated_records.length > 0 && (
                <>
                  <Divider
                    style={{ paddingTop: "1rem", paddingBottom: "1rem" }}
                  >
                    <Typography variant="h6">Updated entities</Typography>
                  </Divider>

                  {entry.entity_updated_records.map((record) => (
                    <EntityCard key={record.ref_id}>
                      <EntitySummaryLink summary={record} />
                    </EntityCard>
                  ))}
                </>
              )}

              {entry.entity_removed_records.length > 0 && (
                <>
                  <Divider
                    style={{ paddingTop: "1rem", paddingBottom: "1rem" }}
                  >
                    <Typography variant="h6">Removed entities</Typography>
                  </Divider>

                  {entry.entity_removed_records.map((record) => (
                    <EntityCard key={record.ref_id}>
                      <EntitySummaryLink summary={record} removed />
                    </EntityCard>
                  ))}
                </>
              )}
            </AccordionDetails>
          </Accordion>
        );
      })}
    </ToolPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error generating tasks! Please try again!`
);

const AccordionHeader = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
}));

const GenTargetsSection = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
  paddingBottom: theme.spacing(1),
}));
