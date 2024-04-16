import type { WorkingMem } from "webapi-client";
import { LinkTag } from "./infra/link-tag";

interface Props {
  workingMem: WorkingMem;
}

export function WorkingMemTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/working-mem/archive/${props.workingMem.ref_id}`}
      label={props.workingMem.name}
      color="primary"
    />
  );
}
