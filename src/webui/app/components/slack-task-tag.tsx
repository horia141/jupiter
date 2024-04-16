import type { SlackTask } from "webapi-client";
import { slackTaskNiceName } from "~/logic/domain/slack-task";
import { LinkTag } from "./infra/link-tag";

interface Props {
  slackTask: SlackTask;
}

export function SlackTaskTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/slack-tasks/${props.slackTask.ref_id}`}
      label={slackTaskNiceName(props.slackTask)}
      color="primary"
    />
  );
}
