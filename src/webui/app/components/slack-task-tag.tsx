import type { SlackTask } from "jupiter-gen";
import { slackTaskNiceName } from "~/logic/domain/slack-task";
import { LinkTag } from "./infra/link-tag";

interface Props {
  slackTask: SlackTask;
}

export function SlackTaskTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/slack-tasks/${props.slackTask.ref_id.the_id}`}
      label={slackTaskNiceName(props.slackTask).the_name}
      color="primary"
    />
  );
}
