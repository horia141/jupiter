import { BigPlanStats } from "@jupiter/webapi-client";

import {
  WidgetContainer,
  WidgetProps,
} from "~/components/domain/application/home/common";
import { sortBigPlansNaturally } from "~/logic/domain/big-plan";
import { StandardDivider } from "~/components/infra/standard-divider";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { BigPlanStack } from "~/components/domain/concept/big-plan/big-plan-stack";

export function KeyBigPlansProgressWidget(props: WidgetProps) {
  const keyBigPlans = props.keyBigPlans!;
  const sortedBigPlans = sortBigPlansNaturally(
    keyBigPlans.bigPlans.map((bp) => bp.bigPlan),
  );
  const bigPlanStatsByRefId: Map<string, BigPlanStats> = new Map(
    keyBigPlans.bigPlans.map((bp) => [bp.bigPlan.ref_id, bp.stats]),
  );

  if (sortedBigPlans.length === 0) {
    return (
      <WidgetContainer>
        <EntityNoNothingCard
          title="No key big plans found"
          message="Mark some big plans as key to see their progress here."
          newEntityLocations="/app/workspace/big-plans/new"
          helpSubject={DocsHelpSubject.BIG_PLANS}
        />
      </WidgetContainer>
    );
  }

  return (
    <WidgetContainer>
      <StandardDivider title="📋 Key Big Plans Progress" size="large" />
      <BigPlanStack
        topLevelInfo={props.topLevelInfo}
        bigPlans={sortedBigPlans}
        bigPlanStatsByRefId={bigPlanStatsByRefId}
        showOptions={{
          showDonePct: true,
          showStatus: true,
          showProject: true,
          showEisen: true,
          showDifficulty: true,
          showActionableDate: true,
          showDueDate: true,
          showHandleMarkDone: false,
          showHandleMarkNotDone: false,
        }}
      />
    </WidgetContainer>
  );
}
