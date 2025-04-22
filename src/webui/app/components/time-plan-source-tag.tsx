import { TimePlanSource } from "@jupiter/webapi-client";

import { timePlanSourceName } from "~/logic/domain/time-plan-source";

import { SlimChip } from "./infra/chips";

interface Props {
  source: TimePlanSource;
}

export function TimePlanSourceTag({ source }: Props) {
  const tagName = timePlanSourceName(source);
  const tagClass = sourceToClass(source);
  return <SlimChip label={tagName} color={tagClass} />;
}

function sourceToClass(source: TimePlanSource): "info" | "warning" {
  switch (source) {
    case TimePlanSource.USER:
      return "info";
    case TimePlanSource.GENERATED:
      return "warning";
  }
}
