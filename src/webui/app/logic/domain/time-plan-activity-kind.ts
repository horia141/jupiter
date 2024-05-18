import { TimePlanActivityKind } from "@jupiter/webapi-client";

export function timePlanActivityKindName(kind: TimePlanActivityKind): string {
  switch (kind) {
    case TimePlanActivityKind.FINISH:
      return "Fisish";
    case TimePlanActivityKind.MAKE_PROGRESS:
      return "Make Progress";
  }
}

const TIME_PLAN_ACTIVITY_KIND_MAP = {
  [TimePlanActivityKind.FINISH]: 0,
  [TimePlanActivityKind.MAKE_PROGRESS]: 1,
};

export function compareTimePlanActivityKind(
  kind1: TimePlanActivityKind,
  kind2: TimePlanActivityKind
): number {
  return (
    TIME_PLAN_ACTIVITY_KIND_MAP[kind1] - TIME_PLAN_ACTIVITY_KIND_MAP[kind2]
  );
}
