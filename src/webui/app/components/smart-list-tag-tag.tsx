import type { SmartListTag } from "jupiter-gen";
import { SlimChip } from "./infra/slim-chip";

interface Props {
  tag: SmartListTag;
}

export function SmartListTagTag({ tag }: Props) {
  return <SlimChip color="success" label={tag.tag_name.the_tag} />;
}
