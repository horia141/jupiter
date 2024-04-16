import { BigPlanStatus } from "webapi-client";
import {
  bigPlanStatusIcon,
  bigPlanStatusName,
} from "~/logic/domain/big-plan-status";
import { SlimChip } from "./infra/chips";

interface Props {
  status: BigPlanStatus;
  format?: "name" | "icon";
}

export function BigPlanStatusTag(props: Props) {
  const format = props.format ?? "name";
  const tagName =
    format === "name"
      ? bigPlanStatusName(props.status)
      : bigPlanStatusIcon(props.status);
  const tagClass = statusToClass(props.status);
  if (format === "name") {
    return <SlimChip label={tagName} color={tagClass} />;
  } else {
    return <span style={{ paddingRight: "0.5rem" }}>{tagName}</span>;
  }
}

function statusToClass(
  status: BigPlanStatus
): "default" | "info" | "warning" | "success" | "error" {
  switch (status) {
    case BigPlanStatus.NOT_STARTED:
      return "default";
    case BigPlanStatus.ACCEPTED:
      return "info";
    case BigPlanStatus.IN_PROGRESS:
      return "warning";
    case BigPlanStatus.BLOCKED:
      return "warning";
    case BigPlanStatus.DONE:
      return "success";
    case BigPlanStatus.NOT_DONE:
      return "error";
  }
}
