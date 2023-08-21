import { ShouldRevalidateFunction } from "@remix-run/react";
import { TrunkCard } from "~/components/infra/trunk-card";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function Subscription() {
  return (
    <TrunkCard>
      <div dangerouslySetInnerHTML={stripeEmbed()} />
    </TrunkCard>
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
