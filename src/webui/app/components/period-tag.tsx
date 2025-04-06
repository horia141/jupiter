import { RecurringTaskPeriod } from "@jupiter/webapi-client";

import { periodName } from "~/logic/domain/period";

import { SlimChip } from "./infra/chips";

interface Props {
  period: RecurringTaskPeriod;
}

export function PeriodTag(props: Props) {
  const tagName = periodName(props.period);
  const tagClass = periodToClass(props.period);
  return <SlimChip label={tagName} color={tagClass} />;
}

function periodToClass(
  period: RecurringTaskPeriod,
): "info" | "success" | "primary" | "warning" | "error" {
  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return "info";
    case RecurringTaskPeriod.WEEKLY:
      return "success";
    case RecurringTaskPeriod.MONTHLY:
      return "primary";
    case RecurringTaskPeriod.QUARTERLY:
      return "warning";
    case RecurringTaskPeriod.YEARLY:
      return "error";
  }
}
