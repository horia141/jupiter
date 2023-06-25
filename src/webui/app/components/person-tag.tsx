import type { Person } from "jupiter-gen";
import { LinkTag } from "./infra/link-tag";

interface Props {
  person: Person;
}

export function PersonTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/persons/${props.person.ref_id.the_id}`}
      label={props.person.name.the_name}
      color="primary"
    />
  );
}
