import { NamedEntityTag } from "@jupiter/webapi-client";

export function entityTagName(entityTag: NamedEntityTag): string {
  switch (entityTag) {
    case NamedEntityTag.SCORE_LOG_ENTRY:
      return "Score Log Entry";
    case NamedEntityTag.HOME_TAB:
      return "Home Tab";
    case NamedEntityTag.HOME_WIDGET:
      return "Home Widget";
    case NamedEntityTag.INBOX_TASK:
      return "Inbox Task";
    case NamedEntityTag.WORKING_MEM:
      return "Working Mem";
    case NamedEntityTag.TIME_PLAN:
      return "Time Plan";
    case NamedEntityTag.TIME_PLAN_ACTIVITY:
      return "Time Plan Activity";
    case NamedEntityTag.SCHEDULE_STREAM:
      return "Schedule Stream";
    case NamedEntityTag.SCHEDULE_EVENT_IN_DAY:
      return "Schedule Event In Day";
    case NamedEntityTag.SCHEDULE_EVENT_FULL_DAYS:
      return "Schedule Event Full Days";
    case NamedEntityTag.SCHEDULE_EXTERNAL_SYNC_LOG:
      return "Schedule External Sync Log";
    case NamedEntityTag.HABIT:
      return "Habit";
    case NamedEntityTag.CHORE:
      return "Chore";
    case NamedEntityTag.BIG_PLAN:
      return "Big Plan";
    case NamedEntityTag.BIG_PLAN_MILESTONE:
      return "Big Plan Milestone";
    case NamedEntityTag.JOURNAL:
      return "Journal";
    case NamedEntityTag.DOC:
      return "Doc";
    case NamedEntityTag.VACATION:
      return "Vacation";
    case NamedEntityTag.PROJECT:
      return "Project";
    case NamedEntityTag.SMART_LIST:
      return "Smart List";
    case NamedEntityTag.SMART_LIST_TAG:
      return "Smart List Tag";
    case NamedEntityTag.SMART_LIST_ITEM:
      return "Smart List Item";
    case NamedEntityTag.METRIC:
      return "Metric";
    case NamedEntityTag.METRIC_ENTRY:
      return "Metric Entry";
    case NamedEntityTag.PERSON:
      return "Person";
    case NamedEntityTag.SLACK_TASK:
      return "Slack Task";
    case NamedEntityTag.EMAIL_TASK:
      return "Email Task";
  }
}
