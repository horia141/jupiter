import { RecurringTaskPeriod } from "@jupiter/webapi-client";
import { Button, ButtonGroup } from "@mui/material";
import { json, LoaderArgs, redirect } from "@remix-run/node";
import { Outlet, ShouldRevalidateFunction, useParams, useTransition } from "@remix-run/react";
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
import { NavMultipleCompact, NavMultipleSpread, NavSingle, SectionActions } from "~/components/infra/section-actions";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";

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

  const nextInterval = DateTime.now();

  return json({
    today: query.today as string,
    period: query.period as RecurringTaskPeriod,
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
  
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

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
                      link: `/workspace/calendar/schedule/event-in-day/new`
                    }),
                    NavSingle({
                      text: "New Event Full Days",
                      link: `/workspace/calendar/schedule/event-full-days/new`
                    }),
                    NavSingle({
                      text: "New Calendar Stream",
                      link: `/workspace/calendar/schedule/stream/new`
                    }),
                    NavSingle({
                      text: "View Calendar Streams",
                      link: `/workspace/calendar/schedule/stream`
                    })
                  ]
                }),
              NavMultipleSpread({
                navs: [
                  NavSingle({
                    text: "Today",
                    link: `/workspace/calendar?today=${DateTime.now().toISODate()}&period=${loaderData.period}`
                  }),
                  NavSingle({
                    icon: <ArrowBackIcon />,
                    link: `/workspace/calendar?today=${DateTime.now().toISODate()}&period=${loaderData.period}`
                  }),
                  NavSingle({
                    icon: <ArrowForwardIcon />,
                    link: `/workspace/calendar?today=${DateTime.now().toISODate()}&period=${loaderData.period}`
                  }),
                ]
              })
            ]}
            /> 
        }
        returnLocation="/workspace">
        For {loaderData.today} and {loaderData.period}
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
            

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
