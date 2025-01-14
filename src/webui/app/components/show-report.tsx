import type {
  InboxTasksSummary,
  ProjectSummary,
  ReportPeriodResult,
  WorkableSummary,
} from "@jupiter/webapi-client";
import {
  InboxTaskSource,
  RecurringTaskPeriod,
  UserFeature,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
import {
  Box,
  Divider,
  List,
  ListItem,
  ListItemText,
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
import { useState } from "react";

import { EntityNameOneLineComponent } from "~/components/entity-name";
import { ScoreOverview } from "~/components/gamification/score-overview";
import { EntityLink } from "~/components/infra/entity-card";
import { aDateToDate } from "~/logic/domain/adate";
import { inboxTaskSourceName } from "~/logic/domain/inbox-task-source";
import { periodName } from "~/logic/domain/period";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { isUserFeatureAvailable } from "~/logic/domain/user";
import {
  inferSourcesForEnabledFeatures,
  isWorkspaceFeatureAvailable,
} from "~/logic/domain/workspace";
import { useBigScreen } from "~/rendering/use-big-screen";
import type { TopLevelInfo } from "~/top-level-context";
import { TabPanel } from "./tab-panel";

const _SOURCES_TO_REPORT = [
  InboxTaskSource.USER,
  InboxTaskSource.HABIT,
  InboxTaskSource.CHORE,
  InboxTaskSource.BIG_PLAN,
  InboxTaskSource.JOURNAL,
  InboxTaskSource.METRIC,
  InboxTaskSource.PERSON_CATCH_UP,
  InboxTaskSource.PERSON_BIRTHDAY,
  InboxTaskSource.SLACK_TASK,
  InboxTaskSource.EMAIL_TASK,
];

interface ShowReportProps {
  topLevelInfo: TopLevelInfo;
  allProjects: ProjectSummary[];
  report: ReportPeriodResult;
}

export function ShowReport({
  topLevelInfo,
  allProjects,
  report,
}: ShowReportProps) {
  const isBigScreen = useBigScreen();
  const [showTab, changeShowTab] = useState(0);

  const tabIndicesMap = {
    global: 0,
    "by-periods": 1,
    "by-projects": 2,
    "by-habits": 3,
    "by-chores": 4,
    "by-big-plans": 5,
  };

  if (
    !isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.PROJECTS
    )
  ) {
    tabIndicesMap["by-habits"] -= 1;
    tabIndicesMap["by-chores"] -= 1;
    tabIndicesMap["by-big-plans"] -= 1;
  }
  if (
    !isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.HABITS
    )
  ) {
    tabIndicesMap["by-chores"] -= 1;
    tabIndicesMap["by-big-plans"] -= 1;
  }
  if (
    !isWorkspaceFeatureAvailable(
      topLevelInfo.workspace,
      WorkspaceFeature.CHORES
    )
  ) {
    tabIndicesMap["by-big-plans"] -= 1;
  }

  const allProjectsSorted = sortProjectsByTreeOrder(allProjects);
  const allProjectsByRefId = new Map<string, ProjectSummary>(
    allProjects.map((p) => [p.ref_id, p])
  );

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

      {isUserFeatureAvailable(topLevelInfo.user, UserFeature.GAMIFICATION) &&
        report.user_score_overview && (
          <>
            <Divider>
              <Typography variant="h6">💪 Score</Typography>
            </Divider>
            <ScoreOverview scoreOverview={report.user_score_overview} />
          </>
        )}

      <Tabs
        value={showTab}
        onChange={(_, newValue) => changeShowTab(newValue)}
        variant={isBigScreen ? "standard" : "scrollable"}
        scrollButtons="auto"
        centered={isBigScreen}
      >
        <Tab label="🌍 Global" />
        <Tab label="⌛ By Periods" />
        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.PROJECTS
        ) && <Tab label="💡 By Projects" />}
        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.HABITS
        ) && <Tab label="💪 By Habits" />}
        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.CHORES
        ) && <Tab label="♻️ By Chore" />}
        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.BIG_PLANS
        ) && <Tab label="🌍 By Big Plan" />}
      </Tabs>

      <TabPanel value={showTab} index={tabIndicesMap["global"]}>
        <OverviewReport
          topLevelInfo={topLevelInfo}
          inboxTasksSummary={report.global_inbox_tasks_summary}
          bigPlansSummary={report.global_big_plans_summary}
        />
      </TabPanel>

      <TabPanel value={showTab} index={tabIndicesMap["by-periods"]}>
        <Stack spacing={2} useFlexGap>
          {report.per_period_breakdown.map((pp) => (
            <Box key={pp.name}>
              <Divider>
                <Typography variant="h5">{pp.name}</Typography>
              </Divider>
              <OverviewReport
                topLevelInfo={topLevelInfo}
                inboxTasksSummary={pp.inbox_tasks_summary}
                bigPlansSummary={pp.big_plans_summary}
              />
            </Box>
          ))}
        </Stack>
      </TabPanel>

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.PROJECTS
      ) && (
        <TabPanel value={showTab} index={tabIndicesMap["by-projects"]}>
          <Stack spacing={2} useFlexGap>
            {allProjectsSorted.map((project) => {
              const pb = report.per_project_breakdown.find(
                (pb) => pb.ref_id === project.ref_id
              );

              if (pb === undefined) {
                return null;
              }

              const fullProjectName = computeProjectHierarchicalNameFromRoot(
                project,
                allProjectsByRefId
              );

              return (
                <Box key={pb.ref_id}>
                  <Divider variant="fullWidth">
                    <Typography
                      variant="h6"
                      sx={{
                        maxWidth: "calc(100vw - 2rem)",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {fullProjectName}
                    </Typography>
                  </Divider>
                  <OverviewReport
                    topLevelInfo={topLevelInfo}
                    inboxTasksSummary={pb.inbox_tasks_summary}
                    bigPlansSummary={pb.big_plans_summary}
                  />
                </Box>
              );
            })}
          </Stack>
        </TabPanel>
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.HABITS
      ) && (
        <TabPanel value={showTab} index={tabIndicesMap["by-habits"]}>
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
                          <TableRow key={`${period}-${phb.ref_id}`}>
                            <SmallTableCell>
                              <EntityLink
                                to={`/workspace/habits/${phb.ref_id}`}
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
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.CHORES
      ) && (
        <TabPanel value={showTab} index={tabIndicesMap["by-chores"]}>
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
                          <TableRow key={`${period}-${pcb.ref_id}`}>
                            <SmallTableCell className="name-value">
                              <EntityLink
                                to={`/workspace/chores/${pcb.ref_id}`}
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
      )}

      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.BIG_PLANS
      ) && (
        <TabPanel value={showTab} index={tabIndicesMap["by-big-plans"]}>
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
                  <TableRow key={pbb.ref_id}>
                    <SmallTableCell className="name-value">
                      <EntityLink to={`/workspace/big-plans/${pbb.ref_id}`}>
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
      )}
    </Stack>
  );
}

interface OverviewReportProps {
  topLevelInfo: TopLevelInfo;
  inboxTasksSummary: InboxTasksSummary;
  bigPlansSummary: WorkableSummary;
}

function OverviewReport(props: OverviewReportProps) {
  const isBigScreen = useBigScreen();
  const filteredSource = inferSourcesForEnabledFeatures(
    props.topLevelInfo.workspace,
    _SOURCES_TO_REPORT
  );

  return (
    <Stack spacing={2} useFlexGap>
      <Divider>
        <Typography variant="h6">📥 Inbox Tasks</Typography>
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
            {filteredSource.map((source) => (
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

      {isWorkspaceFeatureAvailable(
        props.topLevelInfo.workspace,
        WorkspaceFeature.BIG_PLANS
      ) && (
        <>
          <Divider>
            <Typography variant="h6">🌍 Big Plans</Typography>
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
                  <ListItem key={bp.ref_id}>
                    <EntityLink to={`/workspace/big-plans/${bp.ref_id}`}>
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
                  <ListItem key={bp.ref_id}>
                    <EntityLink to={`/workspace/big-plans/${bp.ref_id}`}>
                      <EntityNameOneLineComponent name={bp.name} />
                    </EntityLink>
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </>
      )}
    </Stack>
  );
}

const SmallTableCell = styled(TableCell)`
  font-size: 0.75rem;
`;
