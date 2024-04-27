import type { Chore } from "@jupiter/webapi-client";
import { LinkTag } from "./infra/link-tag";

interface Props {
  chore: Chore;
}

export function ChoreTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/chores/${props.chore.ref_id}`}
      label={props.chore.name}
      color="primary"
    />
  );
}
