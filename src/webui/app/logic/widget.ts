import {
  User,
  WidgetDimension,
  WidgetType,
  WidgetTypeConstraints,
  Workspace,
} from "@jupiter/webapi-client";

export function widgetTypeName(type: WidgetType): string {
  switch (type) {
    case WidgetType.MOTD:
      return "Message of the Day";
    case WidgetType.KEY_HABITS_STREAKS:
      return "Key Habits Streaks";
    case WidgetType.HABIT_INBOX_TASKS:
      return "Habit Tasks";
    case WidgetType.RANDOM_HABIT:
      return "Random Habit";
    case WidgetType.CHORE_INBOX_TASKS:
      return "Chore Tasks";
    case WidgetType.RANDOM_CHORE:
      return "Random Chore";
    case WidgetType.KEY_BIG_PLANS_PROGRESS:
      return "Key Big Plans Progress";
    case WidgetType.UPCOMING_BIRTHDAYS:
      return "Upcoming Birthdays";
    case WidgetType.CALENDAR_DAY:
      return "Calendar For Today";
    case WidgetType.SCHEDULE_DAY:
      return "Schedule For Today";
    case WidgetType.TIME_PLAN_VIEW:
      return "Time Plan View";
    case WidgetType.GAMIFICATION_OVERVIEW:
      return "Gamification Overview";
    case WidgetType.GAMIFICATION_HISTORY_WEEKLY:
      return "Weekly Score History";
    case WidgetType.GAMIFICATION_HISTORY_MONTHLY:
      return "Monthly Score History";
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
    case WidgetDimension.DIM_2X1_SMALL_SCREEN_FLEX:
    case WidgetDimension.DIM_2X2:
    case WidgetDimension.DIM_2X3:
      return 2;
    case WidgetDimension.DIM_3X1:
    case WidgetDimension.DIM_3X1_SMALL_SCREEN_FLEX:
    case WidgetDimension.DIM_3X2:
    case WidgetDimension.DIM_3X3:
      return 3;
  }
}

export function widgetDimensionCols(dimension: WidgetDimension): number {
  switch (dimension) {
    case WidgetDimension.DIM_1X1:
    case WidgetDimension.DIM_2X1:
    case WidgetDimension.DIM_2X1_SMALL_SCREEN_FLEX:
    case WidgetDimension.DIM_3X1:
    case WidgetDimension.DIM_3X1_SMALL_SCREEN_FLEX:
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
  return (
    dimension === WidgetDimension.DIM_KX1 ||
    dimension === WidgetDimension.DIM_KX2 ||
    dimension === WidgetDimension.DIM_KX3
  );
}

export function isWidgetDimensionFlex(dimension: WidgetDimension): boolean {
  return (
    dimension === WidgetDimension.DIM_2X1_SMALL_SCREEN_FLEX ||
    dimension === WidgetDimension.DIM_3X1_SMALL_SCREEN_FLEX
  );
}

export function widgetDimensionName(dimension: WidgetDimension): string {
  if (dimension === WidgetDimension.DIM_2X1_SMALL_SCREEN_FLEX) {
    return `2x1 (small screen flex)`;
  }

  if (dimension === WidgetDimension.DIM_3X1_SMALL_SCREEN_FLEX) {
    return `3x1 (small screen flex)`;
  }

  if (isWidgetDimensionKSized(dimension)) {
    return `kx${widgetDimensionCols(dimension)}`;
  }
  const rows = widgetDimensionRows(dimension);
  const cols = widgetDimensionCols(dimension);

  return `${rows}x${cols}`;
}

export function isAllowedForWidgetConstraints(
  constraints: WidgetTypeConstraints,
  user: User,
  workspace: Workspace,
): boolean {
  // Keep in sync with the logic in the backend in
  // widget.py:is_allowed_for
  if (constraints.only_for_user_features) {
    for (const userFeature of constraints.only_for_user_features) {
      if (!user.feature_flags[userFeature]) {
        return false;
      }
    }
  }

  if (constraints.only_for_workspace_features) {
    for (const workspaceFeature of constraints.only_for_workspace_features) {
      if (!workspace.feature_flags[workspaceFeature]) {
        return false;
      }
    }
  }

  return true;
}
