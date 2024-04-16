import type { EmailTask } from "webapi-client";
import { emailTaskNiceName } from "~/logic/domain/email-task";
import { LinkTag } from "./infra/link-tag";

interface Props {
  emailTask: EmailTask;
}

export function EmailTaskTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/email-tasks/${props.emailTask.ref_id}`}
      label={emailTaskNiceName(props.emailTask)}
      color="primary"
    />
  );
}
