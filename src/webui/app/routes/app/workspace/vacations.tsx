import type { Vacation, VacationFindResultEntry } from "@jupiter/webapi-client";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { Box, IconButton, Typography, styled } from "@mui/material";
import type { CalendarTooltipProps, TimeRangeDayData } from "@nivo/calendar";
import { ResponsiveTimeRange } from "@nivo/calendar";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Outlet, useNavigate } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { useContext, useEffect, useMemo, useState } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { ADateTag } from "~/components/adate-tag";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { aDateToDate } from "~/logic/domain/adate";
import { sortVacationsNaturally } from "~/logic/domain/vacation";
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
  const response = await apiClient.vacations.vacationFind({
    allow_archived: false,
    include_notes: false,
    include_time_event_blocks: false,
  });
  return json(response.entries);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Vacations() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const sortedVacations = sortVacationsNaturally(
    entries.map((e) => e.vacation),
  );
  const vacationsByRefId = new Map<string, VacationFindResultEntry>();
  for (const entry of entries) {
    vacationsByRefId.set(entry.vacation.ref_id, entry);
  }

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const today = DateTime.local({ zone: topLevelInfo.user.timezone }).startOf(
    "day",
  );

  return (
    <TrunkPanel
      key={"vacations"}
      createLocation="/app/workspace/vacations/new"
      returnLocation="/app/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <VacationCalendar today={today} sortedVacations={sortedVacations} />

        {sortedVacations.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no vacations to show. You can create a new vacation."
            newEntityLocations="/app/workspace/vacations/new"
            helpSubject={DocsHelpSubject.VACATIONS}
          />
        )}

        <EntityStack>
          {sortedVacations.map((vacation) => {
            return (
              <EntityCard
                entityId={`vacation-${vacation.ref_id}`}
                key={`vacation-${vacation.ref_id}`}
              >
                <EntityLink to={`/app/workspace/vacations/${vacation.ref_id}`}>
                  <EntityNameComponent name={vacation.name} />
                  <ADateTag label="Start Date" date={vacation.start_date} />
                  <ADateTag
                    label="End Date"
                    date={vacation.end_date}
                    color="success"
                  />
                </EntityLink>
              </EntityCard>
            );
          })}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

interface VacationCalendarProps {
  today: DateTime;
  sortedVacations: Array<Vacation>;
}

function VacationCalendar({ today, sortedVacations }: VacationCalendarProps) {
  const earliestDate =
    sortedVacations.length > 0
      ? aDateToDate(sortedVacations[sortedVacations.length - 1].start_date)
      : today;
  const latestDate =
    sortedVacations.length > 0
      ? aDateToDate(sortedVacations[0].end_date)
      : earliestDate;

  const [vacationDays, vacationsById, data] = useMemo(() => {
    const vacationDays = new Map<string, Set<string>>();
    const vacationsById = new Map<string, Vacation>();

    for (const vacation of sortedVacations) {
      let walker = aDateToDate(vacation.start_date).startOf("day");
      const limit = aDateToDate(vacation.end_date).endOf("day").toISODate();
      while (walker.toISODate() <= limit) {
        const entry = vacationDays.get(walker.toISODate()) || new Set<string>();
        entry.add(vacation.ref_id);
        vacationDays.set(walker.toISODate(), entry);
        walker = walker.plus({ days: 1 });
      }

      vacationsById.set(vacation.ref_id, vacation);
    }

    const data = [];
    let currDate = earliestDate!;

    while (currDate.toISODate() <= latestDate.toISODate()) {
      data.push({
        value: vacationDays.has(currDate.toISODate()) ? 100 : 0,
        day: currDate.toISODate(),
      });
      currDate = currDate.plus({ days: 1 });
    }

    return [vacationDays, vacationsById, data];
  }, [sortedVacations, earliestDate, latestDate]);

  const isBigScreen = useBigScreen();
  const intervalStep = isBigScreen ? "year" : "month";

  const firstIntervalRoundDate = earliestDate.startOf(intervalStep);
  const lastIntervalRoundDate = latestDate.endOf(intervalStep);
  const [currentInterval, setCurrentInterval] = useState(
    lastIntervalRoundDate.startOf(intervalStep),
  );
  useEffect(() => {
    setCurrentInterval(() => lastIntervalRoundDate.startOf(intervalStep));
    // Disabled beacuse eslint is wrong here!
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isBigScreen]);

  const dayClickNavigate = useNavigate();

  function handlePrevInterval() {
    if (currentInterval === firstIntervalRoundDate) {
      return;
    }
    setCurrentInterval((ci) =>
      intervalStep === "year"
        ? ci.minus({ years: 1 })
        : ci.minus({ months: 1 }),
    );
  }

  function handleNextInterval() {
    if (currentInterval === lastIntervalRoundDate) {
      return;
    }
    setCurrentInterval((ci) =>
      intervalStep === "year" ? ci.plus({ years: 1 }) : ci.plus({ months: 1 }),
    );
  }

  function handleDayClick(datum: TimeRangeDayData) {
    if (!vacationDays.has(datum.day)) {
      return null;
    }

    const [theId] = vacationDays.get(datum.day) as Set<string>;
    dayClickNavigate(`/app/workspace/vacations/${theId}`);
  }

  function handleTooltip(props: CalendarTooltipProps) {
    if (!vacationDays.has(props.day)) {
      return null;
    }

    const [theId] = vacationDays.get(props.day) as Set<string>;
    const vacation = vacationsById.get(theId) as Vacation;
    return (
      <TooltipBox
        sx={{
          backgroundColor: "white",
        }}
      >
        {vacation.name}
      </TooltipBox>
    );
  }

  return (
    <StyledDiv>
      <IconButton
        disabled={currentInterval.equals(firstIntervalRoundDate)}
        onClick={handlePrevInterval}
        aria-label="previous-interval"
        size="large"
      >
        <ArrowBackIosNewIcon fontSize="inherit" />
      </IconButton>
      <Box sx={{ minWidth: isBigScreen ? "900px" : "200px" }}>
        <Typography sx={{ textAlign: "center" }}>
          Year {currentInterval.toFormat("yyyy")}
        </Typography>
        <ResponsiveTimeRange
          data={data}
          from={currentInterval.toFormat("yyyy-MM-dd")}
          to={currentInterval.endOf(intervalStep).toFormat("yyyy-MM-dd")}
          weekdayLegendOffset={60}
          weekdayTicks={[0, 1, 2, 3, 4, 5, 6]}
          onClick={handleDayClick}
          tooltip={handleTooltip}
          minValue={0}
          maxValue={100}
          emptyColor="#eeeeee"
          colors={["#eeeeee", "#61cdbb"]}
          align="center"
          margin={{
            top: 40,
            right: isBigScreen ? 100 : 60,
            bottom: 20,
            left: isBigScreen ? 40 : 0,
          }}
        />
      </Box>
      <IconButton
        disabled={currentInterval
          .endOf(intervalStep)
          .equals(lastIntervalRoundDate)}
        onClick={handleNextInterval}
        aria-label="next-interval"
        size="large"
      >
        <ArrowForwardIosIcon fontSize="inherit" />
      </IconButton>
    </StyledDiv>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error loading the vacations! Please try again!`,
});

const TooltipBox = styled("div")`
  font-size: 1rem;
  border: 1px dashed gray;
  padding: 5px;
  border-radius: 5px;
`;

const StyledDiv = styled("div")`
  height: 180px;
  display: flex;
  justify-content: space-between;
  flex-direction: row;
`;
