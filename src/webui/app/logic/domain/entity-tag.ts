import { NamedEntityTag } from "jupiter-gen";

export function entityTagName(entityTag: NamedEntityTag): string {
  switch (entityTag) {
    case NamedEntityTag.INBOX_TASK:
      return "Inbox Task";
    case NamedEntityTag.WORKING_MEM:
      return "Working Mem";
    case NamedEntityTag.HABIT:
      return "Habit";
    case NamedEntityTag.CHORE:
      return "Chore";
    case NamedEntityTag.BIG_PLAN:
      return "Big Plan";
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
