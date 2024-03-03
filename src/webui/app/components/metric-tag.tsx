import type { Metric } from "jupiter-gen";
import { LinkTag } from "./infra/link-tag";

interface Props {
  metric: Metric;
}

export function MetricTag(props: Props) {
  return (
    <LinkTag
      to={`/workspace/metrics/${props.metric.ref_id}/details`}
      label={props.metric.name}
      color="primary"
    />
  );
}
