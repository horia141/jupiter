import { InboxTaskStatus } from "webapi-client";
import { inboxTaskStatusName } from "~/logic/domain/inbox-task-status";
import { SlimChip } from "./infra/chips";

interface Props {
  status: InboxTaskStatus;
}

export function InboxTaskStatusTag(props: Props) {
  const tagName = inboxTaskStatusName(props.status);
  const tagClass = statusToClass(props.status);
  return <SlimChip label={tagName} color={tagClass} />;
}

function statusToClass(
  status: InboxTaskStatus
): "default" | "primary" | "info" | "warning" | "success" | "error" {
  switch (status) {
    case InboxTaskStatus.NOT_STARTED:
      return "default";
    case InboxTaskStatus.ACCEPTED:
      return "primary";
    case InboxTaskStatus.RECURRING:
      return "primary";
    case InboxTaskStatus.IN_PROGRESS:
      return "info";
    case InboxTaskStatus.BLOCKED:
      return "warning";
    case InboxTaskStatus.DONE:
      return "success";
    case InboxTaskStatus.NOT_DONE:
      return "error";
  }
}
