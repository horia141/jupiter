import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  ShouldRevalidateFunction,
  useFetcher,
  useOutlet,
} from "@remix-run/react";
import type { BigPlan, BigPlanFindResultEntry, Project } from "jupiter-gen";
import { BigPlanStatus, WorkspaceFeature } from "jupiter-gen";
import { ADateTag } from "~/components/adate-tag";
import { BigPlanStatusTag } from "~/components/big-plan-status-tag";
import { ProjectTag } from "~/components/project-tag";

import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  styled,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { useContext, useState } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import {
  EntityNameComponent,
  EntityNameOneLineComponent,
} from "~/components/entity-name";
import { ActionHeader } from "~/components/infra/actions-header";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { aDateToDate } from "~/logic/domain/adate";
import { sortBigPlansNaturally } from "~/logic/domain/big-plan";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
  });
  const response = await getLoggedInApiClient(session).bigPlan.findBigPlan({
    allow_archived: false,
    include_project: true,
    include_inbox_tasks: false,
  });
  return json({
    bigPlans: response.entries,
    allProjects: summaryResponse.projects as Array<Project>,
  });
}

enum View {
  TIMELINE_BY_PROJECT = "timeline-by-project",
  TIMELINE = "timeline",
  LIST = "list",
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function BigPlans() {
  const outlet = useOutlet();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const isBigScreen = useBigScreen();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedBigPlans = sortBigPlansNaturally(
    loaderData.bigPlans.map((b) => b.big_plan)
  );
  const entriesByRefId = new Map<string, BigPlanFindResultEntry>();
  for (const entry of loaderData.bigPlans) {
    entriesByRefId.set(entry.big_plan.ref_id.the_id, entry);
  }

  const topLevelInfo = useContext(TopLevelInfoContext);

  const initialView = isWorkspaceFeatureAvailable(
    topLevelInfo.workspace,
    WorkspaceFeature.PROJECTS
  )
    ? View.TIMELINE_BY_PROJECT
    : View.TIMELINE;
  const [selectedView, setSelectedView] = useState(initialView);

  const archiveBigPlanFetch = useFetcher();

  function archiveBigPlan(bigPlan: BigPlan) {
    archiveBigPlanFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
        project: "NOT USED - FOR ARCHIVE ONLY",
        status: BigPlanStatus.ACCEPTED,
      },
      {
        method: "post",
        action: `/workspace/big-plans/${bigPlan.ref_id.the_id}`,
      }
    );
  }

  const [showFilterDialog, setShowFilterDialog] = useState(false);

  return (
    <TrunkPanel>
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          <ButtonGroup>
            <Button
              variant="contained"
              to="/workspace/big-plans/new"
              component={Link}
            >
              Create
            </Button>
          </ButtonGroup>

          {isBigScreen && (
            <ButtonGroup>
              {isWorkspaceFeatureAvailable(
                topLevelInfo.workspace,
                WorkspaceFeature.PROJECTS
              ) && (
                <Button
                  variant={
                    selectedView === View.TIMELINE_BY_PROJECT
                      ? "contained"
                      : "outlined"
                  }
                  onClick={() => setSelectedView(View.TIMELINE_BY_PROJECT)}
                >
                  Timeline by Project
                </Button>
              )}
              <Button
                variant={
                  selectedView === View.TIMELINE ? "contained" : "outlined"
                }
                onClick={() => setSelectedView(View.TIMELINE)}
              >
                Timeline
              </Button>
              <Button
                variant={selectedView === View.LIST ? "contained" : "outlined"}
                onClick={() => setSelectedView(View.LIST)}
              >
                List
              </Button>
            </ButtonGroup>
          )}

          {!isBigScreen && (
            <>
              <ButtonGroup>
                <Button onClick={() => setShowFilterDialog(true)}>
                  Filters
                </Button>
              </ButtonGroup>

              <Dialog
                onClose={() => setShowFilterDialog(false)}
                open={showFilterDialog}
              >
                <DialogTitle>Filters</DialogTitle>
                <DialogContent>
                  <ButtonGroup orientation="vertical">
                    {isWorkspaceFeatureAvailable(
                      topLevelInfo.workspace,
                      WorkspaceFeature.PROJECTS
                    ) && (
                      <Button
                        variant={
                          selectedView === View.TIMELINE_BY_PROJECT
                            ? "contained"
                            : "outlined"
                        }
                        onClick={() =>
                          setSelectedView(View.TIMELINE_BY_PROJECT)
                        }
                      >
                        Timeline by Project
                      </Button>
                    )}
                    <Button
                      variant={
                        selectedView === View.TIMELINE
                          ? "contained"
                          : "outlined"
                      }
                      onClick={() => setSelectedView(View.TIMELINE)}
                    >
                      Timeline
                    </Button>
                    <Button
                      variant={
                        selectedView === View.LIST ? "contained" : "outlined"
                      }
                      onClick={() => setSelectedView(View.LIST)}
                    >
                      List
                    </Button>
                  </ButtonGroup>
                </DialogContent>
                <DialogActions>
                  <Button onClick={() => setShowFilterDialog(false)}>
                    Close
                  </Button>
                </DialogActions>
              </Dialog>
            </>
          )}
        </ActionHeader>

        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.PROJECTS
        ) &&
          selectedView === View.TIMELINE_BY_PROJECT && (
            <>
              {loaderData.allProjects.map((p) => {
                const theProjects = sortedBigPlans.filter(
                  (se) =>
                    entriesByRefId.get(se.ref_id.the_id)?.big_plan
                      .project_ref_id.the_id === p.ref_id.the_id
                );

                if (theProjects.length === 0) {
                  return null;
                }

                return (
                  <Box key={p.ref_id.the_id}>
                    <Divider>
                      <Typography variant="h6">{p.name.the_name}</Typography>
                    </Divider>
                    <>
                      {isBigScreen && (
                        <BigScreenTimeline bigPlans={theProjects} />
                      )}
                      {!isBigScreen && (
                        <SmallScreenTimeline bigPlans={theProjects} />
                      )}
                    </>
                  </Box>
                );
              })}
            </>
          )}

        {selectedView === View.TIMELINE && (
          <>
            {isBigScreen && <BigScreenTimeline bigPlans={sortedBigPlans} />}
            {!isBigScreen && <SmallScreenTimeline bigPlans={sortedBigPlans} />}
          </>
        )}

        {selectedView === View.LIST && (
          <List
            topLevelInfo={topLevelInfo}
            bigPlans={sortedBigPlans}
            entriesByRefId={entriesByRefId}
            onArchiveBigPlan={archiveBigPlan}
          />
        )}
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        {outlet}
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the big plans! Please try again!`
);

interface BigScreenTimelineProps {
  bigPlans: Array<BigPlan>;
}

function BigScreenTimeline({ bigPlans }: BigScreenTimelineProps) {
  return (
    <TableContainer component={Box}>
      <Table sx={{ tableLayout: "fixed" }}>
        <TableHead>
          <TableRow>
            <TableCell width="33%">Name</TableCell>
            <TableCell width="12%">Status</TableCell>
            <TableCell width="55%">Range</TableCell>
          </TableRow>
          <TableRow>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <BigScreenTimelineHeaderCell>
              <span>Jan</span>
              <span>Feb</span>
              <span>Mar</span>
              <span>Apr</span>
              <span>May</span>
              <span>Jun</span>
              <span>Jul</span>
              <span>Aug</span>
              <span>Sep</span>
              <span>Oct</span>
              <span>Nov</span>
              <span>Dec</span>
            </BigScreenTimelineHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {bigPlans.map((entry) => {
            const { leftMargin, width } = computeBigPlanGnattPosition(entry);

            return (
              <TableRow key={entry.ref_id.the_id}>
                <TableCell>
                  <EntityLink
                    to={`/workspace/big-plans/${entry.ref_id.the_id}`}
                  >
                    <EntityNameOneLineComponent name={entry.name} />
                  </EntityLink>
                </TableCell>
                <TableCell>
                  <BigPlanStatusTag status={entry.status} />
                </TableCell>
                <TableCell>
                  <TimelineGnattBlob leftmargin={leftMargin} width={width}>
                    &nbsp;
                  </TimelineGnattBlob>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

const BigScreenTimelineHeaderCell = styled(TableCell)(({ theme }) => ({
  display: "flex",
  flexWrap: "nowrap",
  justifyContent: "space-between",
  flexDirection: "row",
}));

interface SmallScreenTimelineProps {
  bigPlans: Array<BigPlan>;
}

function SmallScreenTimeline({ bigPlans }: SmallScreenTimelineProps) {
  return (
    <EntityStack>
      <SmallScreenTimelineList>
        <SmallScreenTimelineHeader>
          <span>Jan</span>
          <span>Feb</span>
          <span>Mar</span>
          <span>Apr</span>
          <span>May</span>
          <span>Jun</span>
          <span>Jul</span>
          <span>Aug</span>
          <span>Sep</span>
          <span>Oct</span>
          <span>Nov</span>
          <span>Dec</span>
        </SmallScreenTimelineHeader>

        {bigPlans.map((bigPlan) => {
          const { leftMargin, width, betterWidth, betterLeftMargin } =
            computeBigPlanGnattPosition(bigPlan);

          return (
            <SmallScreenTimelineLine key={bigPlan.ref_id.the_id}>
              <TimelineGnattBlob
                isunderlay="true"
                leftmargin={leftMargin}
                width={width}
              >
                &nbsp;
              </TimelineGnattBlob>
              <TimelineLink
                leftmargin={betterLeftMargin}
                width={betterWidth}
                to={`/workspace/big-plans/${bigPlan.ref_id.the_id}`}
              >
                <BigPlanStatusTag status={bigPlan.status} format="icon" />
                <EntityNameOneLineComponent name={bigPlan.name} />
              </TimelineLink>
            </SmallScreenTimelineLine>
          );
        })}
      </SmallScreenTimelineList>
    </EntityStack>
  );
}

const SmallScreenTimelineList = styled("div")(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  gap: "1rem",
  fontSize: "0.8rem",
}));

const SmallScreenTimelineHeader = styled("div")(({ theme }) => ({
  display: "flex",
  justifyContent: "space-between",
  flexWrap: "nowrap",
}));

const SmallScreenTimelineLine = styled("div")(({ theme }) => ({
  position: "relative",
  height: "1.5rem",
}));

interface TimelineGnattBlobProps {
  isunderlay?: string;
  leftmargin: number;
  width: number;
}

const TimelineGnattBlob = styled("div")<TimelineGnattBlobProps>(
  ({ theme, isunderlay, leftmargin, width }) => ({
    position: isunderlay ? "absolute" : "static",
    display: "block",
    marginLeft: `${leftmargin * 100}%`,
    width: `${width * 100}%`,
    backgroundColor: theme.palette.action.disabledBackground,
    borderRadius: "0.25rem",
    height: "1.5rem",
  })
);

interface TimelineLinkProps {
  leftmargin: number;
  width: number;
}

const TimelineLink = styled(Link)<TimelineLinkProps>(
  ({ theme, leftmargin, width }) => ({
    position: "absolute",
    display: "flex",
    marginLeft: `${leftmargin * 100}%`,
    width: `${width * 100}%`,
    paddingLeft: "0.5rem",
    borderRadius: "0.25rem",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    height: "1.5rem",
    lineHeight: "1.5rem",
  })
);

interface ListProps {
  topLevelInfo: TopLevelInfo;
  bigPlans: Array<BigPlan>;
  entriesByRefId: Map<string, BigPlanFindResultEntry>;
  onArchiveBigPlan: (bigPlan: BigPlan) => void;
}

function List({
  topLevelInfo,
  bigPlans,
  entriesByRefId,
  onArchiveBigPlan,
}: ListProps) {
  return (
    <EntityStack>
      {bigPlans.map((entry) => (
        <EntityCard
          key={entry.ref_id.the_id}
          allowSwipe
          allowMarkNotDone
          onMarkNotDone={() => onArchiveBigPlan(entry)}
        >
          <EntityLink to={`/workspace/big-plans/${entry.ref_id.the_id}`}>
            <EntityNameComponent name={entry.name} />
          </EntityLink>
          <Divider />
          <BigPlanStatusTag status={entry.status} />
          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <ProjectTag
              project={
                entriesByRefId.get(entry.ref_id.the_id)?.project as Project
              }
            />
          )}

          {entry.actionable_date && (
            <ADateTag label="Actionable Date" date={entry.actionable_date} />
          )}
          {entry.due_date && (
            <ADateTag label="Due Date" date={entry.due_date} />
          )}
        </EntityCard>
      ))}
    </EntityStack>
  );
}

function computeBigPlanGnattPosition(entry: BigPlan) {
  const startOfYear = DateTime.now().startOf("year");
  // Avoids a really tricky bug on NYE.
  const endOfYear = startOfYear.endOf("year");

  let leftMargin = undefined;
  if (!entry.actionable_date) {
    leftMargin = 0.45;
  } else {
    const actionableDate = aDateToDate(entry.actionable_date);
    if (actionableDate < startOfYear) {
      leftMargin = 0;
    } else if (actionableDate > endOfYear) {
      leftMargin = 1;
    } else {
      leftMargin = actionableDate.ordinal / startOfYear.daysInYear;
    }
  }

  let width = undefined;
  if (!entry.due_date) {
    width = 0.1; // TODO: better here in case there's an actionable_date
  } else {
    const dueDate = aDateToDate(entry.due_date);

    if (dueDate > endOfYear) {
      width = 1 - leftMargin;
    } else if (dueDate < startOfYear) {
      width = 0;
    } else {
      const rightMargin = dueDate.ordinal / startOfYear.daysInYear;
      width = rightMargin - leftMargin;
    }
  }

  const betterWidth = width < 0.4 ? 0.4 : width;
  const betterLeftMargin = leftMargin > 0.6 ? 0.6 : leftMargin;

  return { leftMargin, width, betterWidth, betterLeftMargin };
}
