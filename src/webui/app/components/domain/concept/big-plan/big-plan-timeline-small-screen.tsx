import type {
  ADate,
  BigPlan,
  BigPlanMilestone,
  BigPlanStats,
} from "@jupiter/webapi-client";
import { Tooltip, styled } from "@mui/material";
import { Link } from "@remix-run/react";
import type { DateTime } from "luxon";

import { aDateToDate } from "~/logic/domain/adate";
import { bigPlanDonePct } from "~/logic/domain/big-plan";
import { BigPlanStatusTag } from "~/components/domain/concept/big-plan/big-plan-status-tag";
import { EntityNameOneLineComponent } from "~/components/infra/entity-name";
import { EntityStack } from "~/components/infra/entity-stack";
import { IsKeyTag } from "~/components/domain/core/is-key-tag";

interface DateMarker {
  date: ADate;
  color: string;
  label: string;
}

interface BigPlanTimelineSmallScreenProps {
  thisYear: DateTime;
  bigPlans: Array<BigPlan>;
  bigPlanMilestonesByRefId: Map<string, Array<BigPlanMilestone>>;
  bigPlanStatsByRefId: Map<string, BigPlanStats>;
  dateMarkers?: Array<DateMarker>;
  selectedPredicate?: (it: BigPlan) => boolean;
  allowSelect?: boolean;
  onClick?: (it: BigPlan) => void;
}

export function BigPlanTimelineSmallScreen({
  thisYear,
  bigPlans,
  bigPlanMilestonesByRefId,
  bigPlanStatsByRefId,
  dateMarkers,
  selectedPredicate,
  allowSelect,
  onClick,
}: BigPlanTimelineSmallScreenProps) {
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

        {dateMarkers && dateMarkers.length > 0 && (
          <SmallScreenTimelineLine>
            {dateMarkers.map((marker, idx) => {
              if (idx % 2 === 1) {
                return null;
              }
              const markerPosition = computeMarkerPosition(
                thisYear,
                marker.date,
              );
              return (
                <MarkerLabel key={idx} leftmargin={markerPosition}>
                  {marker.label}
                </MarkerLabel>
              );
            })}
          </SmallScreenTimelineLine>
        )}

        {bigPlans.map((bigPlan) => {
          const { leftMargin, width, betterWidth, betterLeftMargin } =
            computeBigPlanGnattPosition(thisYear, bigPlan);

          const milestones = bigPlanMilestonesByRefId.get(bigPlan.ref_id) || [];

          return (
            <SmallScreenTimelineLine
              key={bigPlan.ref_id}
              selected={allowSelect && selectedPredicate?.(bigPlan)}
              onClick={() => allowSelect && onClick?.(bigPlan)}
            >
              <TimelineGnattBlob
                isunderlay="true"
                leftmargin={leftMargin}
                width={width}
              >
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
                      color={"blue"}
                    />
                  </Tooltip>
                );
              })}
              <TimelineLink
                leftmargin={betterLeftMargin}
                width={betterWidth}
                to={`/app/workspace/big-plans/${bigPlan.ref_id}`}
              >
                <BigPlanStatusTag status={bigPlan.status} format="icon" />
                <IsKeyTag isKey={bigPlan.is_key} />
                <EntityNameOneLineComponent
                  name={`[${bigPlanDonePct(
                    bigPlan,
                    bigPlanStatsByRefId.get(bigPlan.ref_id)!,
                  )}%] ${bigPlan.name}`}
                />
              </TimelineLink>
            </SmallScreenTimelineLine>
          );
        })}

        {dateMarkers && dateMarkers.length > 0 && (
          <SmallScreenTimelineLine>
            {dateMarkers.map((marker, idx) => {
              if (idx % 2 === 0) {
                return null;
              }
              const markerPosition = computeMarkerPosition(
                thisYear,
                marker.date,
              );
              return (
                <MarkerLabel key={idx} leftmargin={markerPosition}>
                  {marker.label}
                </MarkerLabel>
              );
            })}
          </SmallScreenTimelineLine>
        )}
      </SmallScreenTimelineList>
    </EntityStack>
  );
}

const SmallScreenTimelineList = styled("div")(() => ({
  display: "flex",
  flexDirection: "column",
  gap: "1rem",
  fontSize: "0.8rem",
}));

const SmallScreenTimelineHeader = styled("div")(() => ({
  display: "flex",
  justifyContent: "space-between",
  flexWrap: "nowrap",
}));

interface SmallScreenTimelineLineProps {
  selected?: boolean;
}

const SmallScreenTimelineLine = styled("div")<SmallScreenTimelineLineProps>(
  ({ theme, selected }) => ({
    position: "relative",
    height: "1.5rem",
    backgroundColor: selected ? theme.palette.action.hover : "transparent",
  }),
);

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

interface TimelineLinkProps {
  leftmargin: number;
  width: number;
}

const TimelineLink = styled(Link)<TimelineLinkProps>(
  ({ leftmargin, width, theme }) => ({
    textDecoration: "none",
    position: "absolute",
    display: "flex",
    color: theme.palette.info.dark,
    ":visited": {
      color: theme.palette.info.dark,
    },
    marginLeft: `${leftmargin * 100}%`,
    width: `${width * 100}%`,
    paddingLeft: "0.5rem",
    borderRadius: "0.25rem",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    height: "1.5rem",
    lineHeight: "1.5rem",
    zIndex: 2,
  }),
);

interface DateMarkerProps {
  leftmargin: number;
  color: string;
}

const DateMarker = styled("div")<DateMarkerProps>(({ leftmargin, color }) => ({
  position: "absolute",
  bottom: 0,
  top: "-0.5rem",
  height: "calc(100% + 1rem)",
  width: "2px",
  backgroundColor: color,
  left: `${leftmargin * 100}%`,
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
    top: "0px",
    bottom: "0px",
    width: "2px",
    backgroundColor: color,
    left: `${leftmargin * 100}%`,
    zIndex: 1,
    cursor: "pointer",
  }),
);

interface MarkerLabelProps {
  leftmargin: number;
}

const MarkerLabel = styled("div")<MarkerLabelProps>(({ leftmargin }) => ({
  position: "absolute",
  transform: "translateX(-50%)",
  left: `${leftmargin * 100}%`,
  whiteSpace: "nowrap",
  fontWeight: "bold",
}));

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
