import type { ADate, Timestamp } from "@jupiter/webapi-client";
import { DateTime } from "luxon";
import { timestampToDate } from "~/logic/domain/timestamp";
import { FatChip } from "./infra/chips";

interface TimeDiffTagProps {
  labelPrefix: string;
  collectionTime: ADate | Timestamp;
}

export function TimeDiffTag(props: TimeDiffTagProps) {
  const today = DateTime.now().startOf("day");
  const collectionTime = timestampToDate(props.collectionTime);
  const diff = today.diff(collectionTime, ["years", "months", "days"]);

  let diffStr = "";
  if (diff.years > 0) {
    if (diff.years === 1) {
      diffStr += "1 year";
    } else {
      diffStr += `${diff.years} years`;
    }
  }

  if (diff.months > 0) {
    if (diffStr.length > 0) {
      diffStr += ", ";
    }
    if (diff.months === 1) {
      diffStr += "1 month";
    } else {
      diffStr += `${diff.months} months`;
    }
  }

  if (diff.days > 0) {
    if (diffStr.length > 0) {
      diffStr += ", ";
    }
    if (diff.days === 1) {
      diffStr += "1 day";
    } else {
      diffStr += `${diff.days} days`;
    }
  }

  if (diffStr.length === 0) {
    diffStr = "today";
  } else {
    diffStr += " ago";
  }

  return <FatChip label={`${props.labelPrefix} ${diffStr}`} color="info" />;
}
