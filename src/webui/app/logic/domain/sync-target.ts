import { SyncTarget } from "jupiter-gen";

export function syncTargetName(syncTarget: SyncTarget): string {
  switch (syncTarget) {
    case SyncTarget.INBOX_TASKS:
      return "Inbox Tasks";
    case SyncTarget.HABITS:
      return "Habits";
    case SyncTarget.CHORES:
      return "Chores";
    case SyncTarget.BIG_PLANS:
      return "Big Plans";
    case SyncTarget.NOTES:
      return "Notes";
    case SyncTarget.VACATIONS:
      return "Vacations";
    case SyncTarget.PROJECTS:
      return "Projects";
    case SyncTarget.SMART_LISTS:
      return "Smart Lists";
    case SyncTarget.METRICS:
      return "Metrics";
    case SyncTarget.PERSONS:
      return "Persons";
    case SyncTarget.SLACK_TASKS:
      return "Slack Tasks";
    case SyncTarget.EMAIL_TASKS:
      return "Email Tasks";
  }
}
