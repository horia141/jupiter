import type { EmailTask } from "jupiter-gen";
import { emailTaskNiceName } from "~/logic/domain/email-task";
import { LinkTag } from "./infra/link-tag";

interface Props {
  emailTask: EmailTask;
}

export function EmailTaskTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/email-tasks/${props.emailTask.ref_id.the_id}`}
      label={emailTaskNiceName(props.emailTask).the_name}
      color="primary"
    />
  );
}
