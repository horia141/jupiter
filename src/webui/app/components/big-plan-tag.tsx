import type { BigPlan } from "jupiter-gen";
import { LinkTag } from "./infra/link-tag";

interface Props {
  bigPlan: BigPlan;
}

export function BigPlanTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/big-plans/${props.bigPlan.ref_id}`}
      label={props.bigPlan.name}
      color="primary"
    />
  );
}
