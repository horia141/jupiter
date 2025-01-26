import type { EmailTask } from "@jupiter/webapi-client";
import { emailTaskNiceName } from "~/logic/domain/email-task";
import { LinkTag } from "./infra/link-tag";

interface Props {
  emailTask: EmailTask;
}

export function EmailTaskTag(props: Props) {
  return <LinkTag label={emailTaskNiceName(props.emailTask)} color="primary" />;
}
