import type { Person } from "@jupiter/webapi-client";
import { LinkTag } from "./infra/link-tag";

interface Props {
  person: Person;
}

export function PersonTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/persons/${props.person.ref_id}`}
      label={props.person.name}
      color="primary"
    />
  );
}
