import type { ShouldRevalidateFunction } from "@remix-run/react";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TOOL,
};

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Subscription() {
  return (
    <TrunkPanel key={"subscription"} returnLocation="/workspace">
      <div dangerouslySetInnerHTML={stripeEmbed()} />
    </TrunkPanel>
  );
}

function stripeEmbed() {
  return {
    __html: `<script async src="https://js.stripe.com/v3/pricing-table.js"></script>
    <stripe-pricing-table 
            pricing-table-id="prctbl_1NBKbMIKm5Q3OQikUit7iZR4"
            publishable-key="pk_live_51N8n2vIKm5Q3OQikBa5sGCHnuImkhF1P9leup0qeCJwop7EVTshVtOMY0IE0n40OPYeZCGRQEBfoMT4944RJTjuO00NyoSVaai">
        </stripe-pricing-table>`,
  };
}
