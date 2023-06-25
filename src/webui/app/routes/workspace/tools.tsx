import { useOutlet } from "@remix-run/react";
import { ToolPanel } from "~/components/infra/tool-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
import {
  DisplayType,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export default function Tools() {
  const outlet = useOutlet();

  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

  return (
    <TrunkCard>
      <ToolPanel show={shouldShowALeaf}>{outlet}</ToolPanel>
    </TrunkCard>
  );
}
