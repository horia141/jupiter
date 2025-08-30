import { InboxTaskSource } from "@jupiter/webapi-client";

import { inboxTaskSourceName } from "~/logic/domain/inbox-task-source";
import { SlimChip } from "~/components/infra/chips";

interface Props {
  source: InboxTaskSource;
}

export function InboxTaskSourceTag(props: Props) {
  const tagName = inboxTaskSourceName(props.source);
  const tagClass = sourceToClass(props.source);
  return <SlimChip label={tagName} color={tagClass} />;
}

function sourceToClass(source: InboxTaskSource): "info" | "warning" | "error" {
  switch (source) {
    case InboxTaskSource.USER:
      return "info";
    case InboxTaskSource.WORKING_MEM_CLEANUP:
      return "warning";
    case InboxTaskSource.TIME_PLAN:
      return "info";
    case InboxTaskSource.HABIT:
      return "warning";
    case InboxTaskSource.CHORE:
      return "warning";
    case InboxTaskSource.BIG_PLAN:
      return "info";
    case InboxTaskSource.JOURNAL:
      return "info";
    case InboxTaskSource.METRIC:
      return "warning";
    case InboxTaskSource.PERSON_BIRTHDAY:
      return "warning";
    case InboxTaskSource.PERSON_CATCH_UP:
      return "warning";
    case InboxTaskSource.SLACK_TASK:
      return "error";
    case InboxTaskSource.EMAIL_TASK:
      return "error";
  }
}
