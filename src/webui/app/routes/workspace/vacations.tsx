import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Outlet,
  ShouldRevalidateFunction,
  useFetcher,
  useNavigate,
  useOutlet,
} from "@remix-run/react";

import type { Vacation } from "jupiter-gen";

import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { IconButton, styled } from "@mui/material";
import type { CalendarTooltipProps, TimeRangeDayData } from "@nivo/calendar";
import { ResponsiveTimeRange } from "@nivo/calendar";
import { AnimatePresence } from "framer-motion";
import { DateTime } from "luxon";
import { useEffect, useMemo, useState } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { ADateTag } from "~/components/adate-tag";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
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
import { getSession } from "~/sessions";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const response = await getLoggedInApiClient(session).vacation.findVacation({
    allow_archived: false,
  });
  return json(response.vacations);
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Vacations({ request }: LoaderArgs) {
  const vacations = useLoaderDataSafeForAnimation<typeof loader>();
  const outlet = useOutlet();

  const sortedVacations = sortVacationsNaturally(vacations);

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  const archiveVacationFetch = useFetcher();

  function archiveVacation(vacation: Vacation) {
    archiveVacationFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
        startDate: "2023-01-10",
        endDate: "2023-01-20",
      },
      {
        method: "post",
        action: `/workspace/vacations/${vacation.ref_id.the_id}`,
      }
    );
  }

  return (
    <TrunkPanel
      createLocation="/workspace/vacations/new"
      returnLocation="/workspace"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <VacationCalendar sortedVacations={sortedVacations} />

        <EntityStack>
          {sortedVacations.map((vacation) => (
            <EntityCard
              key={vacation.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveVacation(vacation)}
            >
              <EntityLink to={`/workspace/vacations/${vacation.ref_id.the_id}`}>
                <EntityNameComponent name={vacation.name} />
                <ADateTag label="Start Date" date={vacation.start_date} />
                <ADateTag
                  label="End Date"
                  date={vacation.end_date}
                  color="success"
                />
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
  );
}

interface VacationCalendarProps {
  sortedVacations: Array<Vacation>;
}

function VacationCalendar({ sortedVacations }: VacationCalendarProps) {
  const earliestDate =
    sortedVacations.length > 0
      ? aDateToDate(sortedVacations[sortedVacations.length - 1].start_date)
      : DateTime.now();
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
        entry.add(vacation.ref_id.the_id);
        vacationDays.set(walker.toISODate(), entry);
        walker = walker.plus({ days: 1 });
      }

      vacationsById.set(vacation.ref_id.the_id, vacation);
    }

    const data = [];
    let currDate = earliestDate;

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
    lastIntervalRoundDate.startOf(intervalStep)
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
      intervalStep === "year" ? ci.minus({ years: 1 }) : ci.minus({ months: 1 })
    );
  }

  function handleNextInterval() {
    if (currentInterval === lastIntervalRoundDate) {
      return;
    }
    setCurrentInterval((ci) =>
      intervalStep === "year" ? ci.plus({ years: 1 }) : ci.plus({ months: 1 })
    );
  }

  function handleDayClick(
    datum: TimeRangeDayData,
    event: React.SyntheticEvent
  ) {
    if (!vacationDays.has(datum.day)) {
      return null;
    }

    const [theId] = vacationDays.get(datum.day) as Set<string>;
    dayClickNavigate(`/workspace/vacations/${theId}`);
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
        {vacation.name.the_name}
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
      <ResponsiveTimeRange
        data={data}
        from={currentInterval.toFormat("yyyy-MM-dd")}
        to={currentInterval.endOf(intervalStep).toFormat("yyyy-MM-dd")}
        //weekdayLegendOffset={0}
        weekdayTicks={[0, 1, 2, 3, 4, 5, 6]}
        //firstWeekday={"monday"}
        onClick={handleDayClick}
        tooltip={handleTooltip}
        minValue={0}
        maxValue={100}
        emptyColor="#eeeeee"
        colors={["#eeeeee", "#61cdbb"]}
        margin={{ top: 40, right: 40, bottom: 40, left: 40 }}
      />
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the vacations! Please try again!`
);

const TooltipBox = styled("div")`
  font-size: 1rem;
  border: 1px dashed gray;
  padding: 5px;
  border-radius: 5px;
`;

const StyledDiv = styled("div")`
  height: 200px;
  display: flex;
  flex-direction: row;
`;
