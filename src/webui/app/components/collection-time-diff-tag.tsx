import type { ADate } from "jupiter-gen";
import { DateTime } from "luxon";
import { aDateToDate } from "~/logic/domain/adate";
import { SlimChip } from "./infra/slim-chip";

interface CollectionTimeDiffTagProps {
  collectionTime: ADate;
}

export function CollectionTimeDiffTag(props: CollectionTimeDiffTagProps) {
  const today = DateTime.now().startOf("day");
  const diff = today.diff(aDateToDate(props.collectionTime), [
    "years",
    "months",
    "days",
  ]);

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

  return <SlimChip label={`Collected ${diffStr}`} color="info" />;
}
