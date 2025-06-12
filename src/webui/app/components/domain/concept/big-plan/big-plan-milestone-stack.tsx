import { BigPlanMilestone } from "@jupiter/webapi-client";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityNameComponent } from "~/components/infra/entity-name";
import { EntityStack } from "~/components/infra/entity-stack";
import { ADateTag } from "~/components/domain/core/adate-tag";

interface BigPlanMilestoneStackProps {
  milestones: BigPlanMilestone[];
}

export function BigPlanMilestoneStack(props: BigPlanMilestoneStackProps) {
  return (
    <EntityStack>
      {props.milestones.map((milestone) => {
        return (
          <EntityCard
            key={`big-plan-milestone-${milestone.ref_id}`}
            entityId={`big-plan-milestone-${milestone.ref_id}`}
          >
            <EntityLink to={`/app/workspace/big-plans/${milestone.big_plan_ref_id}/milestones/${milestone.ref_id}`}>
              <EntityNameComponent name={milestone.name} />
              <ADateTag label="Date" date={milestone.date} />
            </EntityLink>
          </EntityCard>
        );
      })}
    </EntityStack>
  );
}
