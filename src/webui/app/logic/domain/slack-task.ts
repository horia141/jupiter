import type { EntityName, SlackTask } from "jupiter-gen";

export function slackTaskNiceName(slackTask: SlackTask): EntityName {
  if (slackTask.channel) {
    return {
      the_name: `Respond to @${slackTask.user.the_name} on channel #${slackTask.channel.the_name}`,
    };
  } else {
    return { the_name: `Respond to @${slackTask.user.the_name} in DM` };
  }
}
