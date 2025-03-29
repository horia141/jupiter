import type { SyncTarget } from "@jupiter/webapi-client";
import { syncTargetName } from "~/logic/domain/sync-target";

import { SlimChip } from "./infra/chips";

interface SyncTargetTagProps {
  target: SyncTarget;
}

export function SyncTargetTag(props: SyncTargetTagProps) {
  const tagName = syncTargetName(props.target);
  return <SlimChip label={tagName} color="info" />;
}
