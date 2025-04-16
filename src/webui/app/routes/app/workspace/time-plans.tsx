import {
  RecurringTaskPeriod,
  TimePlan,
  type TimePlanFindResultEntry,
} from "@jupiter/webapi-client";
import { Button, Stack } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { TimePlanCard } from "~/components/time-plan-card";
import { TimePlanStack } from "~/components/time-plan-stack";
import {
  findTimePlansThatAreActive,
  sortTimePlansNaturally,
} from "~/logic/domain/time-plan";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.timePlans.timePlanFind({
    allow_archived: false,
    include_notes: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function TimePlans() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const rightNow = DateTime.local({ zone: topLevelInfo.user.timezone }).startOf(
    "day",
  );

  const activeTimePlans = findTimePlansThatAreActive(
    entries.map((e) => e.time_plan),
    rightNow,
  );
  const yearTimePlan = activeTimePlans.find(
    (tp) => tp.period === RecurringTaskPeriod.YEARLY,
  );
  const quarterTimePlan = activeTimePlans.find(
    (tp) => tp.period === RecurringTaskPeriod.QUARTERLY,
  );
  const monthTimePlan = activeTimePlans.find(
    (tp) => tp.period === RecurringTaskPeriod.MONTHLY,
  );
  const weekTimePlan = activeTimePlans.find(
    (tp) => tp.period === RecurringTaskPeriod.WEEKLY,
  );
  const dayTimePlan = activeTimePlans.find(
    (tp) => tp.period === RecurringTaskPeriod.DAILY,
  );
  const sortedTimePlans = sortTimePlansNaturally(
    entries.map((e) => e.time_plan),
  );
  const entriesByRefId = new Map<string, TimePlanFindResultEntry>();
  for (const entry of entries) {
    entriesByRefId.set(entry.time_plan.ref_id, entry);
  }

  return (
    <TrunkPanel
      key={"time-plans"}
      createLocation="/app/workspace/time-plans/new"
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        {sortedTimePlans.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no time plans to show. You can create a new time plan."
            newEntityLocations="/app/workspace/time-plans/new"
            helpSubject={DocsHelpSubject.TIME_PLANS}
          />
        )}

        <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
          <CurrentTimePlan
            today={rightNow}
            period={RecurringTaskPeriod.YEARLY}
            topLevelInfo={topLevelInfo}
            timePlan={yearTimePlan}
            label="Yearly Time Plan"
          />

          <CurrentTimePlan
            today={rightNow}
            period={RecurringTaskPeriod.QUARTERLY}
            topLevelInfo={topLevelInfo}
            timePlan={quarterTimePlan}
            label="Quarterly Time Plan"
          />

          <CurrentTimePlan
            today={rightNow}
            period={RecurringTaskPeriod.MONTHLY}
            topLevelInfo={topLevelInfo}
            timePlan={monthTimePlan}
            label="Monthly Time Plan"
          />

          <CurrentTimePlan
            today={rightNow}
            period={RecurringTaskPeriod.WEEKLY}
            topLevelInfo={topLevelInfo}
            timePlan={weekTimePlan}
            label="Weekly Time Plan"
          />

          <CurrentTimePlan
            today={rightNow}
            period={RecurringTaskPeriod.DAILY}
            topLevelInfo={topLevelInfo}
            timePlan={dayTimePlan}
            label="Daily Time Plan"
          />
        </Stack>

        <TimePlanStack
          label="All Time Plans"
          topLevelInfo={topLevelInfo}
          timePlans={sortedTimePlans}
        />
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

interface CurrentTimePlanProps {
  label: string;
  today: DateTime;
  period: RecurringTaskPeriod;
  timePlan?: TimePlan;
  topLevelInfo: TopLevelInfo;
}

function CurrentTimePlan(props: CurrentTimePlanProps) {
  if (!props.timePlan) {
    return (
      <Button
        variant="outlined"
        component={Link}
        to={`/app/workspace/time-plans/new?initialPeriod=${props.period}&initialRightNow=${props.today.toISODate()}`}
      >
        Create a {props.label}
      </Button>
    );
  }

  return (
    <TimePlanCard
      key={`time-plan-${props.timePlan.ref_id}`}
      topLevelInfo={props.topLevelInfo}
      timePlan={props.timePlan}
      label={props.label}
      showOptions={{
        showSource: false,
        showPeriod: false,
      }}
    />
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the time plans! Please try again!`,
});
