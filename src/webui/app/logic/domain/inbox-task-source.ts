import { InboxTaskSource } from "jupiter-gen";

export function inboxTaskSourceName(source: InboxTaskSource): string {
  switch (source) {
    case InboxTaskSource.USER:
      return "User";
    case InboxTaskSource.WORKING_MEM_CLEANUP:
      return "Working Mem Cleanup";
    case InboxTaskSource.HABIT:
      return "Habit";
    case InboxTaskSource.CHORE:
      return "Chore";
    case InboxTaskSource.BIG_PLAN:
      return "Big Plan";
    case InboxTaskSource.JOURNAL:
      return "Journal";
    case InboxTaskSource.METRIC:
      return "Metric";
    case InboxTaskSource.PERSON_CATCH_UP:
      return "Catch Up";
    case InboxTaskSource.PERSON_BIRTHDAY:
      return "Birthday";
    case InboxTaskSource.SLACK_TASK:
      return "Slack";
    case InboxTaskSource.EMAIL_TASK:
      return "Email";
  }
}
