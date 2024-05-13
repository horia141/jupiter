export function timePlanActivityKindName(kind: TimePlanActivityKind): string {
    switch (kind) {
        case TimePlanActivityKind.FINISH:
            return "Fisish";
        case TimePlanActivityKind.MAKE_PROGRESS:
            return "Make Progress";
    }
}