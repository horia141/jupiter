import type { WorkingMem } from "@jupiter/webapi-client";
import { LinkTag } from "./infra/link-tag";

interface Props {
  workingMem: WorkingMem;
}

export function WorkingMemTag(props: Props) {
  return <LinkTag label={props.workingMem.name} color="primary" />;
}
