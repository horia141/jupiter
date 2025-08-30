import type {
  ADate,
  BigPlan,
  BigPlanMilestone,
  BigPlanStats,
} from "@jupiter/webapi-client";
import {
  Box,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  styled,
  useTheme,
} from "@mui/material";
import type { DateTime } from "luxon";

import { aDateToDate } from "~/logic/domain/adate";
import { bigPlanDonePct } from "~/logic/domain/big-plan";
import { BigPlanStatusTag } from "~/components/domain/concept/big-plan/big-plan-status-tag";
import { EntityNameOneLineComponent } from "~/components/infra/entity-name";
import { EntityLink } from "~/components/infra/entity-card";
import { EisenTag } from "~/components/domain/core/eisen-tag";
import { DifficultyTag } from "~/components/domain/core/difficulty-tag";
import { BigPlanDonePctTag } from "~/components/domain/concept/big-plan/big-plan-done-pct-tag";
import { IsKeyTag } from "~/components/domain/core/is-key-tag";

interface DateMarker {
  date: ADate;
  color: string;
  label: string;
}

interface BigPlanTimelineBigScreenProps {
  thisYear: DateTime;
  bigPlans: Array<BigPlan>;
  bigPlanMilestonesByRefId: Map<string, Array<BigPlanMilestone>>;
  bigPlanStatsByRefId: Map<string, BigPlanStats>;
  dateMarkers?: Array<DateMarker>;
  selectedPredicate?: (it: BigPlan) => boolean;
  allowSelect?: boolean;
  onClick?: (it: BigPlan) => void;
}

export function BigPlanTimelineBigScreen({
  thisYear,
  bigPlans,
  bigPlanMilestonesByRefId,
  bigPlanStatsByRefId,
  dateMarkers,
  selectedPredicate,
  allowSelect,
  onClick,
}: BigPlanTimelineBigScreenProps) {
  const theme = useTheme();
  return (
    <TableContainer component={Box}>
      <Table sx={{ tableLayout: "fixed" }}>
        <TableHead>
          <TableRow>
            <TableCell width="20%">Name</TableCell>
            <TableCell width="25%">Properties</TableCell>
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
            const { leftMargin, width } = computeBigPlanGnattPosition(
              thisYear,
              entry,
            );

            const milestones = bigPlanMilestonesByRefId.get(entry.ref_id) ?? [];

            return (
              <TableRow key={entry.ref_id}>
                <TableCell
                  sx={{
                    padding: "0px",
                    backgroundColor:
                      allowSelect && selectedPredicate?.(entry)
                        ? theme.palette.action.hover
                        : "transparent",
                  }}
                  onClick={() => allowSelect && onClick?.(entry)}
                >
                  <EntityLink
                    block={allowSelect}
                    to={`/app/workspace/big-plans/${entry.ref_id}`}
                    singleLine
                  >
                    <IsKeyTag isKey={entry.is_key} />
                    <EntityNameOneLineComponent name={entry.name} />
                  </EntityLink>
                </TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5}>
                    <BigPlanDonePctTag
                      donePct={bigPlanDonePct(
                        entry,
                        bigPlanStatsByRefId.get(entry.ref_id)!,
                      )}
                    />
                    <BigPlanStatusTag status={entry.status} />
                    <EisenTag eisen={entry.eisen} />
                    <DifficultyTag difficulty={entry.difficulty} />
                  </Stack>
                </TableCell>
                <TableCell sx={{ position: "relative" }}>
                  <TimelineGnattBlob leftmargin={leftMargin} width={width}>
                    &nbsp;
                  </TimelineGnattBlob>
                  {dateMarkers?.map((marker, idx) => {
                    const markerPosition = computeMarkerPosition(
                      thisYear,
                      marker.date,
                    );
                    return (
                      <Tooltip key={idx} title={marker.label} placement="top">
                        <DateMarker
                          leftmargin={markerPosition}
                          color={marker.color}
                        />
                      </Tooltip>
                    );
                  })}
                  {milestones.map((milestone, idx) => {
                    const markerPosition = computeMarkerPosition(
                      thisYear,
                      milestone.date,
                    );
                    return (
                      <Tooltip key={idx} title={milestone.name} placement="top">
                        <MilestoneMarker
                          leftmargin={markerPosition}
                          color="blue"
                        />
                      </Tooltip>
                    );
                  })}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

const BigScreenTimelineHeaderCell = styled(TableCell)(() => ({
  display: "flex",
  flexWrap: "nowrap",
  justifyContent: "space-between",
  flexDirection: "row",
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
  }),
);

interface DateMarkerProps {
  leftmargin: number;
  color: string;
}

const DateMarker = styled("div")<DateMarkerProps>(({ leftmargin, color }) => ({
  position: "absolute",
  top: 0,
  bottom: "-1px",
  width: "2px",
  backgroundColor: color,
  left: `calc(${leftmargin * 100}% - 0.5rem)`,
  zIndex: 1,
  cursor: "pointer",
}));

interface MilestoneMarkerProps {
  leftmargin: number;
  color: string;
}

const MilestoneMarker = styled("div")<MilestoneMarkerProps>(
  ({ leftmargin, color }) => ({
    position: "absolute",
    top: "1rem",
    bottom: "1rem",
    width: "2px",
    backgroundColor: color,
    left: `calc(${leftmargin * 100}% - 0.5rem)`,
    zIndex: 1,
    cursor: "pointer",
  }),
);

function computeMarkerPosition(thisYear: DateTime, date: ADate): number {
  const startOfYear = thisYear.startOf("year");
  const endOfYear = startOfYear.endOf("year");
  const markerDate = aDateToDate(date);

  if (markerDate < startOfYear) {
    return 0;
  } else if (markerDate > endOfYear) {
    return 1;
  } else {
    return markerDate.ordinal / startOfYear.daysInYear;
  }
}

function computeBigPlanGnattPosition(thisYear: DateTime, entry: BigPlan) {
  const startOfYear = thisYear.startOf("year");
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
