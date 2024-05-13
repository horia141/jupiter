import { timePlanActivityKindName } from "~/logic/domain/time-plan-activity-kind";
import { SlimChip } from "./infra/chips";

interface TimePlanActivityKindTagProps {
    kind: TimePlanActivityKind;
}

export function TimePlanActivityKindTag(props: TimePlanActivityKindTagProps) {
    return (
        <SlimChip
            label={timePlanActivityKindName(props.kind)}
            color={kindToColor(props.kind)} />
    );
}

function kindToColor(props: TimePlanActivityKind): "success" | "info" {
    switch (props) {
        case TimePlanActivityKind.FINISH:
            return "success";
        case TimePlanActivityKind.PROGRESS:
            return "info";
    }
}
