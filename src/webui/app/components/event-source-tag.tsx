import type { EventSource } from "@jupiter/webapi-client";
import { eventSourceName } from "~/logic/domain/event-source";
import { SlimChip } from "./infra/chips";

interface Props {
  source: EventSource;
}

export function EventSourceTag(props: Props) {
  const tagName = eventSourceName(props.source);
  return <SlimChip label={tagName} color="info" />;
}
