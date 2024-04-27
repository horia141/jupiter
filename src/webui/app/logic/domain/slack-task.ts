import type { EntityName, SlackTask } from "@jupiter/webapi-client";

export function slackTaskNiceName(slackTask: SlackTask): EntityName {
  if (slackTask.channel) {
    return `Respond to @${slackTask.user} on channel #${slackTask.channel}`;
  } else {
    return `Respond to @${slackTask.user} in DM`;
  }
}
