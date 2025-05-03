import type { SlackTask } from "@jupiter/webapi-client";

import { slackTaskNiceName } from "~/logic/domain/slack-task";
import { LinkTag } from "~/components/infra/link-tag";

interface Props {
  slackTask: SlackTask;
}

export function SlackTaskTag(props: Props) {
  return <LinkTag label={slackTaskNiceName(props.slackTask)} color="primary" />;
}
