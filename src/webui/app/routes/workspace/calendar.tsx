import { RecurringTaskPeriod } from "@jupiter/webapi-client";
import { json, redirect } from "@remix-run/node";
import { Outlet } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { z } from "zod";
import { parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

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
    return redirect(`/workspace/calendar?today=${today}&period=${period}`);
  }

  const response = await getLoggedInApiClient(
    session
  ).calendar.calendarLoadForDateAndPeriod({
    right_now: query.today,
    period: query.period,
  });

  return json({
    scheduleEventInDayEntries: response.schedule_event_in_day_entries,
    scheduleEventFullDayEntries: response.schedule_event_full_day_entries,
    inboxTaskEntries: response.inbox_task_entries,
    personEntries: response.person_entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Schedules() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  return (
    <TrunkPanel key="schedules" returnLocation="/workspace">
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack></EntityStack>
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
