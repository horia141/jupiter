import type { SmartListTag } from "@jupiter/webapi-client";

import { SlimChip } from "./infra/chips";

interface Props {
  tag: SmartListTag;
}

export function SmartListTagTag({ tag }: Props) {
  return <SlimChip color="success" label={tag.tag_name} />;
}
