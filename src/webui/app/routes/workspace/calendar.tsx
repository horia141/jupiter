import { RecurringTaskPeriod } from "@jupiter/webapi-client";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import type { LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useSearchParams, useTransition } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import {
  NavMultipleCompact,
  NavMultipleSpread,
  NavSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { periodName } from "~/logic/domain/period";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TRUNK,
};

const QuerySchema = {
  today: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  period: z.nativeEnum(RecurringTaskPeriod).optional(),
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);

  if (query.today === undefined || query.period === undefined) {
    const today = DateTime.now().toISODate();
    const period = RecurringTaskPeriod.WEEKLY;
    return redirect(`${request.url}?today=${today}&period=${period}`);
  }

  const response = await getLoggedInApiClient(
    session
  ).calendar.calendarLoadForDateAndPeriod({
    right_now: query.today,
    period: query.period,
  });

  return json({
    today: query.today as string,
    period: query.period as RecurringTaskPeriod,
    prevPeriodStartDate: response.prev_period_start_date,
    nextPeriodStartDate: response.next_period_start_date,
    scheduleEventInDayEntries: response.schedule_event_in_day_entries,
    scheduleEventFullDayEntries: response.schedule_event_full_days_entries,
    inboxTaskEntries: response.inbox_task_entries,
    personEntries: response.person_entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Schedules() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const transition = useTransition();
  const [query, _] = useSearchParams();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  return (
    <TrunkPanel
      key="calendar"
      createLocation="/workspace/calendar/schedule/event-in-day/new"
      actions={
        <SectionActions
          id="calendar"
          topLevelInfo={topLevelInfo}
          inputsEnabled={inputsEnabled}
          actions={[
            NavMultipleCompact({
              navs: [
                NavSingle({
                  text: "New Event In Day",
                  link: `/workspace/calendar/schedule/event-in-day/new?${query}`,
                }),
                NavSingle({
                  text: "New Event Full Days",
                  link: `/workspace/calendar/schedule/event-full-days/new?${query}`,
                }),
                NavSingle({
                  text: "New Calendar Stream",
                  link: `/workspace/calendar/schedule/stream/new?${query}`,
                }),
                NavSingle({
                  text: "View Calendar Streams",
                  link: `/workspace/calendar/schedule/stream?${query}`,
                }),
              ],
            }),
            NavMultipleSpread({
              navs: [
                NavSingle({
                  text: "Today",
                  link: `/workspace/calendar?today=${DateTime.now().toISODate()}&period=${
                    loaderData.period
                  }`,
                }),
                NavSingle({
                  text: "Prev",
                  icon: <ArrowBackIcon />,
                  link: `/workspace/calendar?today=${loaderData.prevPeriodStartDate}&period=${loaderData.period}`,
                }),
                NavSingle({
                  text: "Next",
                  icon: <ArrowForwardIcon />,
                  link: `/workspace/calendar?today=${loaderData.nextPeriodStartDate}&period=${loaderData.period}`,
                }),
              ],
            }),
            NavMultipleCompact({
              navs: [
                NavSingle({
                  text: periodName(RecurringTaskPeriod.DAILY),
                  highlight: loaderData.period === RecurringTaskPeriod.DAILY,
                  link: `/workspace/calendar?today=${loaderData.today}&period=${RecurringTaskPeriod.DAILY}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.WEEKLY),
                  highlight: loaderData.period === RecurringTaskPeriod.WEEKLY,
                  link: `/workspace/calendar?today=${loaderData.today}&period=${RecurringTaskPeriod.WEEKLY}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.MONTHLY),
                  highlight: loaderData.period === RecurringTaskPeriod.MONTHLY,
                  link: `/workspace/calendar?today=${loaderData.today}&period=${RecurringTaskPeriod.MONTHLY}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.QUARTERLY),
                  highlight:
                    loaderData.period === RecurringTaskPeriod.QUARTERLY,
                  link: `/workspace/calendar?today=${loaderData.today}&period=${RecurringTaskPeriod.QUARTERLY}`,
                }),
                NavSingle({
                  text: periodName(RecurringTaskPeriod.YEARLY),
                  highlight: loaderData.period === RecurringTaskPeriod.YEARLY,
                  link: `/workspace/calendar?today=${loaderData.today}&period=${RecurringTaskPeriod.YEARLY}`,
                }),
              ],
            }),
          ]}
        />
      }
      returnLocation="/workspace"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        <EntityStack>
          For {loaderData.today} and {loaderData.period}
        </EntityStack>
      </NestingAwareBlock>
      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the calendar events! Please try again!`
);
