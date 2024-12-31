import type { ADate, Timestamp } from "@jupiter/webapi-client";
import type { DateTime } from "luxon";
import { timestampToDate } from "~/logic/domain/timestamp";
import { FatChip } from "./infra/chips";
import { ClientOnly } from "remix-utils";

interface TimeDiffTagProps {
  today: DateTime;
  labelPrefix: string;
  collectionTime: ADate | Timestamp;
}

export function TimeDiffTag(props: TimeDiffTagProps) {
  const today = props.today.startOf("day");
  const collectionTime = timestampToDate(props.collectionTime);
  const diff = today.diff(collectionTime, ["years", "months", "days"]);

  const diffYears = Math.ceil(diff.years);
  const diffMonths = Math.ceil(diff.months);
  const diffDays = Math.ceil(diff.days);

  let diffStr = "";
  if (diffYears > 0) {
    if (diffYears === 1) {
      diffStr += "1 year";
    } else {
      diffStr += `${diffYears} years`;
    }
  }

  if (diffMonths > 0) {
    if (diffStr.length > 0) {
      diffStr += ", ";
    }
    if (diffMonths === 1) {
      diffStr += "1 month";
    } else {
      diffStr += `${diffMonths} months`;
    }
  }

  if (diffDays > 0) {
    if (diffStr.length > 0) {
      diffStr += ", ";
    }
    if (diffDays === 1) {
      diffStr += "1 day";
    } else {
      diffStr += `${diffDays} days`;
    }
  }

  if (diffStr.length === 0) {
    diffStr = "today";
  } else {
    diffStr += " ago";
  }

  return <ClientOnly fallback={<></>}>
    {() => <FatChip label={`${props.labelPrefix} ${diffStr}`} color="info" />}
  </ClientOnly>;
}
