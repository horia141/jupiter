import { InboxTaskStatus } from "webapi-client";

export function inboxTaskStatusIcon(status: InboxTaskStatus): string {
  switch (status) {
    case InboxTaskStatus.NOT_STARTED:
      return "📥";
    case InboxTaskStatus.RECURRING:
      return "🔧";
    case InboxTaskStatus.ACCEPTED:
      return "🔧";
    case InboxTaskStatus.IN_PROGRESS:
      return "🚧";
    case InboxTaskStatus.BLOCKED:
      return "🚧";
    case InboxTaskStatus.NOT_DONE:
      return "⛔";
    case InboxTaskStatus.DONE:
      return "✅";
  }
}

export function inboxTaskStatusName(status: InboxTaskStatus): string {
  switch (status) {
    case InboxTaskStatus.NOT_STARTED:
      return "Not Started";
    case InboxTaskStatus.RECURRING:
      return "Recurring";
    case InboxTaskStatus.ACCEPTED:
      return "Accepted";
    case InboxTaskStatus.IN_PROGRESS:
      return "In Progress";
    case InboxTaskStatus.BLOCKED:
      return "Blocked";
    case InboxTaskStatus.NOT_DONE:
      return "Not Done";
    case InboxTaskStatus.DONE:
      return "Done";
  }
}

export function isCompleted(status: InboxTaskStatus): boolean {
  return status === InboxTaskStatus.DONE || status === InboxTaskStatus.NOT_DONE;
}
