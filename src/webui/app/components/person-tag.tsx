import type { Person } from "@jupiter/webapi-client";

import { LinkTag } from "./infra/link-tag";

interface Props {
  person: Person;
}

export function PersonTag(props: Props) {
  return <LinkTag label={props.person.name} color="primary" />;
}
