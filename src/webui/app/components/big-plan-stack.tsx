import { TopLevelInfo } from "~/top-level-context";
import { EntityStack } from "./infra/entity-stack";
import { ProjectTag } from "./project-tag";

interface BigPlanStackProps {
    topLevelInfo: TopLevelInfo;
    showLabel?: boolean;
    label?: string;
    bigPlans: BigPlan[];
    entriesByRefId?: Map<string, BigPlanFindResultEntry>;
    onCardMarkDone?: (it: BigPlan) => void;
    onCardMarkNotDone?: (it: BigPlan) => void;
}

export function BigPlanStack(props: BigPlanStackProps) { 
    return (
        <EntityStack>
            {props.showLabel && (
              <Divider style={{ paddingTop: "0.5rem" }}>
                <Typography variant="h6">{props.label}</Typography>
              </Divider>
            )}

            {props.bigPlans.map((entry) => (
                <EntityCard
                    key={`big-plan-${entry.ref_id}`}
                    entityId={`big-plan-${entry.ref_id}`}
                    allowSwipe
                    allowMarkDone
                    allowMarkNotDone
                    onMarkDone={() => props.onCardMarkDone && props.onCardMarkDone(entry)}
                    onMarkNotDone={() => props.onCardMarkNotDone && props.onCardMarkNotDone(entry)}
                    >
                    <EntityLink to={`/workspace/big-plans/${entry.ref_id}`}>
                        <EntityNameComponent name={entry.name} />
                    </EntityLink>
                    <Divider />
                    <BigPlanStatusTag status={entry.status} />
                    {isWorkspaceFeatureAvailable(
                        topLevelInfo.workspace,
                        WorkspaceFeature.PROJECTS
                    ) && props.entriesByRefId && (
                        <ProjectTag
                        project={props.entriesByRefId.get(entry.ref_id)?.project as Project}
                        />
                    )}

                    {entry.actionable_date && (
                        <ADateTag label="Actionable Date" date={entry.actionable_date} />
                    )}
                    {entry.due_date && (
                        <ADateTag label="Due Date" date={entry.due_date} />
                    )}
                </EntityCard>
            ))}
        </EntityStack>
    )
}