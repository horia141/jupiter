import type { ADate } from "@jupiter/webapi-client";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import ViewListIcon from "@mui/icons-material/ViewList";
import ViewTimelineIcon from "@mui/icons-material/ViewTimeline";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet } from "@remix-run/react";

import {
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import React, { useContext, useState } from "react";
import { getLoggedInApiClient } from "~/api-clients.server";
import { BigPlanStack } from "~/components/big-plan-stack";
import { BigPlanTimelineBigScreen } from "~/components/big-plan-timeline-big-screen";
import { BigPlanTimelineSmallScreen } from "~/components/big-plan-timeline-small-screen";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { StandardDivider } from "~/components/standard-divider";
import type { BigPlanParent } from "~/logic/domain/big-plan";
import {
  bigPlanFindEntryToParent,
  sortBigPlansNaturally,
} from "~/logic/domain/big-plan";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });
  const response = await apiClient.bigPlans.bigPlanFind({
    allow_archived: false,
    include_project: true,
    include_inbox_tasks: false,
    include_notes: false,
  });
  return json({
    bigPlans: response.entries,
    allProjects: summaryResponse.projects || undefined,
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
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const isBigScreen = useBigScreen();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const sortedBigPlans = sortBigPlansNaturally(
    loaderData.bigPlans.map((b) => b.big_plan),
  );
  const entriesByRefId = new Map<string, BigPlanParent>();
  for (const entry of loaderData.bigPlans) {
    entriesByRefId.set(entry.big_plan.ref_id, bigPlanFindEntryToParent(entry));
  }

  const topLevelInfo = useContext(TopLevelInfoContext);

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone });
  const theRealToday = rightNow.toISODate() as ADate;

  const initialView = isWorkspaceFeatureAvailable(
    topLevelInfo.workspace,
    WorkspaceFeature.PROJECTS,
  )
    ? View.TIMELINE_BY_PROJECT
    : View.TIMELINE;
  const [selectedView, setSelectedView] = useState(initialView);

  const [showFilterDialog, setShowFilterDialog] = useState(false);

  let extraControls = [];
  if (isBigScreen) {
    extraControls = [
      <ButtonGroup key="1">
        {isWorkspaceFeatureAvailable(
          topLevelInfo.workspace,
          WorkspaceFeature.PROJECTS,
        ) && (
          <Button
            variant={
              selectedView === View.TIMELINE_BY_PROJECT
                ? "contained"
                : "outlined"
            }
            startIcon={<ViewTimelineIcon />}
            onClick={() => setSelectedView(View.TIMELINE_BY_PROJECT)}
          >
            Timeline by Project
          </Button>
        )}
        <Button
          variant={selectedView === View.TIMELINE ? "contained" : "outlined"}
          startIcon={<ViewTimelineIcon />}
          onClick={() => setSelectedView(View.TIMELINE)}
        >
          Timeline
        </Button>
        <Button
          variant={selectedView === View.LIST ? "contained" : "outlined"}
          startIcon={<ViewListIcon />}
          onClick={() => setSelectedView(View.LIST)}
        >
          List
        </Button>
      </ButtonGroup>,
    ];
  } else {
    extraControls = [
      <Button
        key="1"
        variant="outlined"
        startIcon={<ViewTimelineIcon />}
        onClick={() => setShowFilterDialog(true)}
      >
        Views
      </Button>,
    ];
  }

  const thisYear = DateTime.local({ zone: topLevelInfo.user.timezone }).startOf(
    "year",
  );
  const sortedProjects = sortProjectsByTreeOrder(loaderData.allProjects || []);
  const allProjectsByRefId = new Map(
    loaderData.allProjects?.map((p) => [p.ref_id, p]),
  );

  return (
    <TrunkPanel
      key={"big-plans"}
      createLocation="/app/workspace/big-plans/new"
      extraControls={extraControls}
      returnLocation="/app/workspace"
    >
      <Dialog
        onClose={() => setShowFilterDialog(false)}
        open={showFilterDialog}
      >
        <DialogTitle>Filters</DialogTitle>
        <DialogContent>
          <ButtonGroup orientation="vertical">
            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS,
            ) && (
              <Button
                variant={
                  selectedView === View.TIMELINE_BY_PROJECT
                    ? "contained"
                    : "outlined"
                }
                startIcon={<ViewTimelineIcon />}
                onClick={() => setSelectedView(View.TIMELINE_BY_PROJECT)}
              >
                Timeline by Project
              </Button>
            )}
            <Button
              variant={
                selectedView === View.TIMELINE ? "contained" : "outlined"
              }
              startIcon={<ViewTimelineIcon />}
              onClick={() => setSelectedView(View.TIMELINE)}
            >
              Timeline
            </Button>
            <Button
              variant={selectedView === View.LIST ? "contained" : "outlined"}
              startIcon={<ViewListIcon />}
              onClick={() => setSelectedView(View.LIST)}
            >
              List
            </Button>
          </ButtonGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowFilterDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {sortedBigPlans.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no big plans to show. You can create a new big plan."
            newEntityLocations="/app/workspace/big-plans/new"
            helpSubject={DocsHelpSubject.BIG_PLANS}
          />
        )}

        {sortedBigPlans.length > 0 &&
          isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS,
          ) &&
          selectedView === View.TIMELINE_BY_PROJECT && (
            <>
              {sortedProjects.map((p) => {
                const theBigPlans = sortedBigPlans.filter(
                  (se) =>
                    entriesByRefId.get(se.ref_id)?.project?.ref_id === p.ref_id,
                );

                if (theBigPlans.length === 0) {
                  return null;
                }

                const fullProjectName = computeProjectHierarchicalNameFromRoot(
                  p,
                  allProjectsByRefId,
                );

                return (
                  <React.Fragment key={p.ref_id}>
                    <StandardDivider title={fullProjectName} size="large" />
                    <>
                      {isBigScreen && (
                        <BigPlanTimelineBigScreen
                          thisYear={thisYear}
                          bigPlans={theBigPlans}
                          dateMarkers={[
                            {
                              date: theRealToday,
                              color: "red",
                              label: "Today",
                            },
                          ]}
                        />
                      )}
                      {!isBigScreen && (
                        <BigPlanTimelineSmallScreen
                          thisYear={thisYear}
                          bigPlans={theBigPlans}
                          dateMarkers={[
                            {
                              date: theRealToday,
                              color: "red",
                              label: "Today",
                            },
                          ]}
                        />
                      )}
                    </>
                  </React.Fragment>
                );
              })}
            </>
          )}

        {sortedBigPlans.length > 0 && selectedView === View.TIMELINE && (
          <>
            {isBigScreen && (
              <BigPlanTimelineBigScreen
                thisYear={thisYear}
                bigPlans={sortedBigPlans}
                dateMarkers={[
                  {
                    date: theRealToday,
                    color: "red",
                    label: "Today",
                  },
                ]}
              />
            )}
            {!isBigScreen && (
              <BigPlanTimelineSmallScreen
                thisYear={thisYear}
                bigPlans={sortedBigPlans}
                dateMarkers={[
                  {
                    date: theRealToday,
                    color: "red",
                    label: "Today",
                  },
                ]}
              />
            )}
          </>
        )}

        {sortedBigPlans.length > 0 && selectedView === View.LIST && (
          <BigPlanStack
            topLevelInfo={topLevelInfo}
            bigPlans={sortedBigPlans}
            entriesByRefId={entriesByRefId}
            showOptions={{
              showStatus: true,
              showParent: true,
              showActionableDate: true,
              showDueDate: true,
              showHandleMarkDone: false,
              showHandleMarkNotDone: false,
            }}
          />
        )}
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary(
  "/app/workspace",
  {
    error: () => `There was an error loading the big plans! Please try again!`,
  },
);
