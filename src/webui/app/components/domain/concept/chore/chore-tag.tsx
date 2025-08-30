import type { Chore } from "@jupiter/webapi-client";

import { LinkTag } from "~/components/infra/link-tag";

interface Props {
  chore: Chore;
}

export function ChoreTag(props: Props) {
  return <LinkTag label={props.chore.name} color="primary" />;
}
