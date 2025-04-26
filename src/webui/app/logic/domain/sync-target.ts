import { SyncTarget } from "@jupiter/webapi-client";

export function syncTargetName(syncTarget: SyncTarget): string {
  switch (syncTarget) {
    case SyncTarget.INBOX_TASKS:
      return "Inbox Tasks";
    case SyncTarget.WORKING_MEM:
      return "Working Mem";
    case SyncTarget.TIME_PLANS:
      return "Time Plans";
    case SyncTarget.SCHEDULE:
      return "Schedule";
    case SyncTarget.HABITS:
      return "Habits";
    case SyncTarget.CHORES:
      return "Chores";
    case SyncTarget.BIG_PLANS:
      return "Big Plans";
    case SyncTarget.JOURNALS:
      return "Journals";
    case SyncTarget.DOCS:
      return "Docs";
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
    case SyncTarget.GAMIFICATION:
      return "Gamification";
  }
}
