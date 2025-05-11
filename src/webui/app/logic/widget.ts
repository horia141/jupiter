import { WidgetDimension, WidgetType } from "@jupiter/webapi-client";

export function widgetTypeName(type: WidgetType): string {
    switch (type) {
        case WidgetType.MOTD:
            return "Message of the Day";
        case WidgetType.WORKING_MEM:
            return "Working Memory";
        case WidgetType.KEY_HABITS_STREAKS:
            return "Key Habits Streaks";
        case WidgetType.HABIT_INBOX_TASKS:
            return "Habit Tasks";
        case WidgetType.CALENDAR_DAY:
            return "Calendar For Today";
    }
}

export function widgetDimensionRows(dimension: WidgetDimension): number {
    switch (dimension) {
        case WidgetDimension.DIM_1X1:
        case WidgetDimension.DIM_1X2:
        case WidgetDimension.DIM_1X3:
        case WidgetDimension.DIM_KX1:
        case WidgetDimension.DIM_KX2:
        case WidgetDimension.DIM_KX3:
            return 1;
        case WidgetDimension.DIM_2X1:
        case WidgetDimension.DIM_2X2:
        case WidgetDimension.DIM_2X3:
            return 2;
        case WidgetDimension.DIM_3X1:
        case WidgetDimension.DIM_3X2:
        case WidgetDimension.DIM_3X3:
            return 3;
    }
}

export function widgetDimensionCols(dimension: WidgetDimension): number {
    switch (dimension) {
        case WidgetDimension.DIM_1X1:
        case WidgetDimension.DIM_2X1:
        case WidgetDimension.DIM_3X1:
        case WidgetDimension.DIM_KX1:
            return 1;
        case WidgetDimension.DIM_1X2:
        case WidgetDimension.DIM_2X2:
        case WidgetDimension.DIM_3X2:
        case WidgetDimension.DIM_KX2:
            return 2;
        case WidgetDimension.DIM_1X3:
        case WidgetDimension.DIM_2X3:
        case WidgetDimension.DIM_3X3:
        case WidgetDimension.DIM_KX3:
            return 3;
    }
}

export function isWidgetDimensionKSized(dimension: WidgetDimension): boolean {
    return dimension === WidgetDimension.DIM_KX1 ||
           dimension === WidgetDimension.DIM_KX2 ||
           dimension === WidgetDimension.DIM_KX3;
} 