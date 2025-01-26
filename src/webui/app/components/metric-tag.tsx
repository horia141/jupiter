import type { Metric } from "@jupiter/webapi-client";
import { LinkTag } from "./infra/link-tag";

interface Props {
  metric: Metric;
}

export function MetricTag(props: Props) {
  return <LinkTag label={props.metric.name} color="primary" />;
}
