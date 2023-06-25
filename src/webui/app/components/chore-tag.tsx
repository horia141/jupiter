import type { Chore } from "jupiter-gen";
import { LinkTag } from "./infra/link-tag";

interface Props {
  chore: Chore;
}

export function ChoreTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/chores/${props.chore.ref_id.the_id}`}
      label={props.chore.name.the_name}
      color="primary"
    />
  );
}
