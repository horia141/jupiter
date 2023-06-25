import type { SelectChangeEvent } from "@mui/material";
import {
  Box,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  Divider,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
  styled,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import type {
  InboxTasksSummary,
  ReportResult,
  WorkableSummary,
} from "jupiter-gen";
import { ApiError, InboxTaskSource, RecurringTaskPeriod } from "jupiter-gen";
import { DateTime } from "luxon";
import { useState } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { TabPanel } from "../../../components/tab-panel";

import { getLoggedInApiClient } from "~/api-clients";
import { EntityNameOneLineComponent } from "~/components/entity-name";
import { EntityLink } from "~/components/infra/entity-card";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { ToolCard } from "~/components/infra/tool-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { inboxTaskSourceName } from "~/logic/domain/inbox-task-source";
import {
  comparePeriods,
  oneLessThanPeriod,
  periodName,
} from "~/logic/domain/period";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const QuerySchema = {
  today: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  period: z.nativeEnum(RecurringTaskPeriod).optional(),
  breakdownPeriod: z
    .union([z.nativeEnum(RecurringTaskPeriod), z.literal("none")])
    .optional(),
};

const ReportFormSchema = {
  today: z.string().optional(),
  period: z.nativeEnum(RecurringTaskPeriod),
  breakdownPeriod: z.union([
    z.nativeEnum(RecurringTaskPeriod),
    z.literal("none"),
  ]),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { today, period, breakdownPeriod } = parseQuery(request, QuerySchema);

  if (
    today === undefined ||
    period === undefined ||
    breakdownPeriod === undefined
  ) {
    return json({ report: undefined });
  }

  const reportResponse = await getLoggedInApiClient(session).report.report({
    today: {
      the_date: today,
      the_datetime: undefined,
    },
    period: period,
    breakdown_period: breakdownPeriod !== "none" ? breakdownPeriod : undefined,
  });

  return json({
    report: reportResponse,
  });
}

export async function action({ request }: ActionArgs) {
  const form = await parseForm(request, ReportFormSchema);

  try {
    const today =
      form.today !== undefined && form.today.trim() !== ""
        ? form.today
        : DateTime.now().toFormat("yyyy-MM-dd");
    return redirect(
      `/workspace/tools/report?today=${today}&period=${form.period}&breakdownPeriod=${form.breakdownPeriod}`
    );
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

export default function Report() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>() as {
    report: ReportResult | undefined;
  };
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const [period, setPeriod] = useState(RecurringTaskPeriod.MONTHLY);
  const [breakdownPeriod, setBreakdownPeriod] = useState<
    RecurringTaskPeriod | "none"
  >(RecurringTaskPeriod.WEEKLY);

  const inputsEnabled = transition.state === "idle";

  function handleChangePeriod(event: SelectChangeEvent<RecurringTaskPeriod>) {
    const newPeriod = event.target.value as RecurringTaskPeriod;
    setPeriod(newPeriod);
    if (newPeriod === RecurringTaskPeriod.DAILY) {
      setBreakdownPeriod("none");
    } else {
      setBreakdownPeriod(oneLessThanPeriod(newPeriod));
    }
  }

  function handleChangeBreakdownPeriod(
    event: SelectChangeEvent<RecurringTaskPeriod | "none">
  ) {
    setBreakdownPeriod(event.target.value as RecurringTaskPeriod | "none");
  }

  return (
    <ToolCard returnLocation="/workspace">
      <GlobalError actionResult={actionData} />
      <Card>
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="today">Today</InputLabel>
              <OutlinedInput
                type="date"
                label="Today"
                name="today"
                defaultValue={
                  loaderData.report?.today.the_date ??
                  DateTime.now().toISODate()
                }
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/today" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="period">Period</InputLabel>
              <Select
                labelId="period"
                name="period"
                readOnly={!inputsEnabled}
                value={period}
                onChange={handleChangePeriod}
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

            <FormControl fullWidth>
              <InputLabel id="breakdownPeriod">Breakdown Period</InputLabel>
              <Select
                labelId="breakdownPeriod"
                name="breakdownPeriod"
                readOnly={!inputsEnabled}
                value={breakdownPeriod}
                onChange={handleChangeBreakdownPeriod}
                label="Breakdown Period"
              >
                <MenuItem value="none">None</MenuItem>
                {Object.values(RecurringTaskPeriod).map((s) => (
                  <MenuItem
                    disabled={comparePeriods(s, period) >= 0}
                    key={s}
                    value={s}
                  >
                    {periodName(s)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/breakdown_period"
              />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Run Report
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      {loaderData && loaderData.report !== undefined && (
        <ShowReport report={loaderData.report} />
      )}
    </ToolCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error running the report! Please try again!`
);

const _SOURCES_TO_REPORT = [
  InboxTaskSource.USER,
  InboxTaskSource.HABIT,
  InboxTaskSource.CHORE,
  InboxTaskSource.BIG_PLAN,
  InboxTaskSource.METRIC,
  InboxTaskSource.PERSON_CATCH_UP,
  InboxTaskSource.PERSON_BIRTHDAY,
  InboxTaskSource.SLACK_TASK,
  InboxTaskSource.EMAIL_TASK,
];

interface ShowReportProps {
  report: ReportResult;
}

function ShowReport({ report }: ShowReportProps) {
  const isBigScreen = useBigScreen();
  const [showTab, changeShowTab] = useState(0);

  return (
    <Stack spacing={2} useFlexGap sx={{ paddingTop: "1rem" }}>
      <Box sx={{ width: "100%", display: "flex", fontSize: "0.2rem" }}>
        <Typography
          variant="h5"
          sx={{
            textOverflow: "ellipsis",
            overflow: "hidden",
            whiteSpace: "nowrap",
          }}
        >
          🚀 {periodName(report.period)} as of{" "}
          {aDateToDate(report.today).toFormat("yyyy-MM-dd")}
        </Typography>
      </Box>

      <Tabs
        value={showTab}
        onChange={(_, newValue) => changeShowTab(newValue)}
        variant={isBigScreen ? "standard" : "scrollable"}
        scrollButtons="auto"
        centered={isBigScreen}
      >
        <Tab label="🌍 Global" />
        <Tab label="💡 By Projects" />
        <Tab label="⌛ By Periods" />
        <Tab label="💪 By Habits" />
        <Tab label="♻️ By Chore" />
        <Tab label="🌍 By Big Plan" />
      </Tabs>

      <TabPanel value={showTab} index={0}>
        <OverviewReport
          inboxTasksSummary={report.global_inbox_tasks_summary}
          bigPlansSummary={report.global_big_plans_summary}
        />
      </TabPanel>

      <TabPanel value={showTab} index={1}>
        <Stack spacing={2} useFlexGap>
          {report.per_project_breakdown.map((pb) => (
            <Box key={pb.ref_id.the_id}>
              <Divider>
                <Typography variant="h5">{pb.name.the_name}</Typography>
              </Divider>
              <OverviewReport
                inboxTasksSummary={pb.inbox_tasks_summary}
                bigPlansSummary={pb.big_plans_summary}
              />
            </Box>
          ))}
        </Stack>
      </TabPanel>

      <TabPanel value={showTab} index={2}>
        <Stack spacing={2} useFlexGap>
          {report.per_period_breakdown.map((pp) => (
            <Box key={pp.name.the_name}>
              <Divider>
                <Typography variant="h5">{pp.name.the_name}</Typography>
              </Divider>
              <OverviewReport
                inboxTasksSummary={pp.inbox_tasks_summary}
                bigPlansSummary={pp.big_plans_summary}
              />
            </Box>
          ))}
        </Stack>
      </TabPanel>

      <TabPanel value={showTab} index={3}>
        <Stack spacing={2} useFlexGap>
          {Object.values(RecurringTaskPeriod).map((period) => {
            const periodHabits = report.per_habit_breakdown.filter(
              (phb) => phb.period === period
            );

            if (periodHabits.length === 0) {
              return null;
            }

            return (
              <Box key={period}>
                <Divider>
                  <Typography variant="h5">{periodName(period)}</Typography>
                </Divider>
                <TableContainer component={Box}>
                  <Table sx={{ tableLayout: "fixed" }}>
                    <TableHead>
                      <TableRow>
                        <SmallTableCell width={isBigScreen ? "20%" : "50%"}>
                          Name
                        </SmallTableCell>
                        {isBigScreen && (
                          <SmallTableCell className="streak-column">
                            Streak
                          </SmallTableCell>
                        )}
                        <SmallTableCell width="10%">
                          📥 {isBigScreen && "Created"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          🔧 {isBigScreen && "Accepted"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          🚧 {isBigScreen && "Working"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          ⛔ {isBigScreen && "Not Done"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          ✅ {isBigScreen && "Done"}
                        </SmallTableCell>
                      </TableRow>
                    </TableHead>

                    <TableBody>
                      {periodHabits.map((phb) => (
                        <TableRow key={`${period}-${phb.ref_id.the_id}`}>
                          <SmallTableCell>
                            <EntityLink
                              to={`/workspace/habits/${phb.ref_id.the_id}`}
                            >
                              <EntityNameOneLineComponent name={phb.name} />
                            </EntityLink>
                          </SmallTableCell>
                          {isBigScreen && (
                            <SmallTableCell>
                              {phb.summary.streak_plot
                                ?.split("")
                                .reverse()
                                .join("")}
                            </SmallTableCell>
                          )}
                          <SmallTableCell>
                            {phb.summary.created_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {phb.summary.accepted_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {phb.summary.working_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {phb.summary.not_done_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {phb.summary.done_cnt}
                          </SmallTableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            );
          })}
        </Stack>
      </TabPanel>

      <TabPanel value={showTab} index={4}>
        <Stack spacing={2} useFlexGap>
          {Object.values(RecurringTaskPeriod).map((period) => {
            const periodChores = report.per_chore_breakdown.filter(
              (pcb) => pcb.period === period
            );

            if (periodChores.length === 0) {
              return null;
            }

            return (
              <Box key={period}>
                <Divider>
                  <Typography variant="h5">{periodName(period)}</Typography>
                </Divider>
                <TableContainer component={Box}>
                  <Table sx={{ tableLayout: "fixed" }}>
                    <TableHead>
                      <TableRow>
                        <SmallTableCell width="50%">Name</SmallTableCell>
                        <SmallTableCell width="10%">
                          📥 {isBigScreen && "Created"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          🔧 {isBigScreen && "Accepted"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          🚧 {isBigScreen && "Working"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          ⛔ {isBigScreen && "Not Done"}
                        </SmallTableCell>
                        <SmallTableCell width="10%">
                          ✅ {isBigScreen && "Done"}
                        </SmallTableCell>
                      </TableRow>
                    </TableHead>

                    <TableBody>
                      {periodChores.map((pcb) => (
                        <TableRow key={`${period}-${pcb.ref_id.the_id}`}>
                          <SmallTableCell className="name-value">
                            <EntityLink
                              to={`/workspace/chores/${pcb.ref_id.the_id}`}
                            >
                              <EntityNameOneLineComponent name={pcb.name} />
                            </EntityLink>
                          </SmallTableCell>
                          <SmallTableCell>
                            {pcb.summary.created_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {pcb.summary.accepted_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {pcb.summary.working_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {pcb.summary.not_done_cnt}
                          </SmallTableCell>
                          <SmallTableCell>
                            {pcb.summary.done_cnt}
                          </SmallTableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            );
          })}
        </Stack>
      </TabPanel>

      <TabPanel value={showTab} index={5}>
        <TableContainer component={Box}>
          <Table sx={{ tableLayout: "fixed" }}>
            <TableHead>
              <TableRow>
                <SmallTableCell width="50%">Name</SmallTableCell>
                <SmallTableCell width="10%">
                  📥 {isBigScreen && "Created"}
                </SmallTableCell>
                <SmallTableCell width="10%">
                  🔧 {isBigScreen && "Accepted"}
                </SmallTableCell>
                <SmallTableCell width="10%">
                  🚧 {isBigScreen && "Working"}
                </SmallTableCell>
                <SmallTableCell width="10%">
                  ⛔ {isBigScreen && "Not Done"}
                </SmallTableCell>
                <SmallTableCell width="10%">
                  ✅ {isBigScreen && "Done"}
                </SmallTableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {report.per_big_plan_breakdown.map((pbb) => (
                <TableRow key={pbb.ref_id.the_id}>
                  <SmallTableCell className="name-value">
                    <EntityLink
                      to={`/workspace/big-plans/${pbb.ref_id.the_id}`}
                    >
                      <EntityNameOneLineComponent name={pbb.name} />
                    </EntityLink>
                  </SmallTableCell>
                  <SmallTableCell>{pbb.summary.created_cnt}</SmallTableCell>
                  <SmallTableCell>{pbb.summary.accepted_cnt}</SmallTableCell>
                  <SmallTableCell>{pbb.summary.working_cnt}</SmallTableCell>
                  <SmallTableCell>{pbb.summary.not_done_cnt}</SmallTableCell>
                  <SmallTableCell>{pbb.summary.done_cnt}</SmallTableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
    </Stack>
  );
}

interface OverviewReportProps {
  inboxTasksSummary: InboxTasksSummary;
  bigPlansSummary: WorkableSummary;
}

function OverviewReport(props: OverviewReportProps) {
  const isBigScreen = useBigScreen();

  return (
    <Stack spacing={2} useFlexGap>
      <Divider>
        <Typography variant="h6">Inbox Tasks</Typography>
      </Divider>
      <TableContainer>
        <Table sx={{ tableLayout: "fixed " }}>
          <TableHead>
            <TableRow>
              <SmallTableCell width="50%">Name</SmallTableCell>
              <SmallTableCell width="10%">
                📥 {isBigScreen && "Created"}
              </SmallTableCell>
              <SmallTableCell width="10%">
                🔧 {isBigScreen && "Accepted"}
              </SmallTableCell>
              <SmallTableCell width="10%">
                🚧 {isBigScreen && "Working"}
              </SmallTableCell>
              <SmallTableCell width="10%">
                ⛔ {isBigScreen && "Not Done"}
              </SmallTableCell>
              <SmallTableCell width="10%">
                ✅ {isBigScreen && "Done"}
              </SmallTableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            <TableRow>
              <SmallTableCell>Total</SmallTableCell>
              <SmallTableCell>
                {props.inboxTasksSummary.created.total_cnt}
              </SmallTableCell>
              <SmallTableCell>
                {props.inboxTasksSummary.accepted.total_cnt}
              </SmallTableCell>
              <SmallTableCell>
                {props.inboxTasksSummary.working.total_cnt}
              </SmallTableCell>
              <SmallTableCell>
                {props.inboxTasksSummary.not_done.total_cnt}
              </SmallTableCell>
              <SmallTableCell>
                {props.inboxTasksSummary.done.total_cnt}
              </SmallTableCell>
            </TableRow>
            {_SOURCES_TO_REPORT.map((source) => (
              <TableRow key={source}>
                <SmallTableCell>{inboxTaskSourceName(source)}</SmallTableCell>
                <SmallTableCell>
                  {props.inboxTasksSummary.created.per_source_cnt.find(
                    (s) => s.source === source
                  )?.count || 0}
                </SmallTableCell>
                <SmallTableCell>
                  {props.inboxTasksSummary.accepted.per_source_cnt.find(
                    (s) => s.source === source
                  )?.count || 0}
                </SmallTableCell>
                <SmallTableCell>
                  {props.inboxTasksSummary.working.per_source_cnt.find(
                    (s) => s.source === source
                  )?.count || 0}
                </SmallTableCell>
                <SmallTableCell>
                  {props.inboxTasksSummary.not_done.per_source_cnt.find(
                    (s) => s.source === source
                  )?.count || 0}
                </SmallTableCell>
                <SmallTableCell>
                  {props.inboxTasksSummary.done.per_source_cnt.find(
                    (s) => s.source === source
                  )?.count || 0}
                </SmallTableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Divider>
        <Typography variant="h6">Big Plans</Typography>
      </Divider>

      <Typography variant="h6">Summary</Typography>

      <List>
        <ListItem>
          <ListItemText
            primary={`📥 Created: ${props.bigPlansSummary.created_cnt}`}
          />{" "}
        </ListItem>
        <ListItem>
          <ListItemText
            primary={`🔧 Accepted: ${props.bigPlansSummary.accepted_cnt}`}
          />
        </ListItem>
        <ListItem>
          <ListItemText
            primary={`🚧 Working: ${props.bigPlansSummary.working_cnt}`}
          />
        </ListItem>
        <ListItem>
          <ListItemText
            primary={`⛔ Not Done: ${props.bigPlansSummary.not_done_cnt}`}
          />
        </ListItem>
        <ListItem>
          <ListItemText
            primary={`✅ Done: ${props.bigPlansSummary.done_cnt}`}
          />
        </ListItem>
      </List>

      {props.bigPlansSummary.not_done_big_plans.length > 0 && (
        <>
          <Typography variant="h6">⛔ Not Done Details</Typography>

          <List>
            {props.bigPlansSummary.not_done_big_plans.map((bp) => (
              <ListItem key={bp.ref_id.the_id}>
                <EntityLink to={`/workspace/big-plans/${bp.ref_id.the_id}`}>
                  <EntityNameOneLineComponent name={bp.name} />
                </EntityLink>
              </ListItem>
            ))}
          </List>
        </>
      )}

      {props.bigPlansSummary.done_big_plans.length > 0 && (
        <>
          <Typography variant="h6">✅ Done Details</Typography>

          <List>
            {props.bigPlansSummary.done_big_plans.map((bp) => (
              <ListItem key={bp.ref_id.the_id}>
                <EntityLink to={`/workspace/big-plans/${bp.ref_id.the_id}`}>
                  <EntityNameOneLineComponent name={bp.name} />
                </EntityLink>
              </ListItem>
            ))}
          </List>
        </>
      )}
    </Stack>
  );
}

const SmallTableCell = styled(TableCell)`
  font-size: 0.75rem;
`;
