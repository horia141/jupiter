import type {
  BigPlan,
  Chore,
  Eisen,
  EmailTask,
  EntityId,
  Habit,
  InboxTask,
  InboxTaskFindResultEntry,
  Metric,
  Person,
  Project,
  RecurringTaskPeriod,
  SlackTask,
} from "@jupiter/webapi-client";
import {
  Difficulty,
  InboxTaskSource,
  InboxTaskStatus,
} from "@jupiter/webapi-client";
import type { DateTime } from "luxon";
import { aDateToDate, compareADate } from "./adate";
import { compareDifficulty } from "./difficulty";
import { compareEisen } from "./eisen";

export interface InboxTaskOptimisticState {
  status: InboxTaskStatus;
  eisen?: Eisen;
}

export interface InboxTaskParent {
  project?: Project;
  bigPlan?: BigPlan;
  habit?: Habit;
  chore?: Chore;
  metric?: Metric;
  person?: Person;
  slackTask?: SlackTask;
  emailTask?: EmailTask;
}

export function inboxTaskFindEntryToParent(
  entry: InboxTaskFindResultEntry,
): InboxTaskParent {
  return {
    project: entry.project,
    bigPlan: entry.big_plan ?? undefined,
    habit: entry.habit ?? undefined,
    chore: entry.chore ?? undefined,
    metric: entry.metric ?? undefined,
    person: entry.person ?? undefined,
    slackTask: entry.slack_task ?? undefined,
    emailTask: entry.email_task ?? undefined,
  };
}

interface InboxTaskFilterOptions {
  allowArchived?: boolean;
  allowSources?: InboxTaskSource[];
  allowProjects?: EntityId[];
  allowStatuses?: InboxTaskStatus[];
  allowEisens?: Eisen[];
  allowDifficulties?: Difficulty[];
  includeIfNoActionableDate?: boolean;
  actionableDateStart?: DateTime;
  actionableDateEnd?: DateTime;
  includeIfNoDueDate?: boolean;
  dueDateStart?: DateTime;
  dueDateEnd?: DateTime;
  allowPeriodsIfHabit?: RecurringTaskPeriod[];
  allowPeriodsIfChore?: RecurringTaskPeriod[];
}

export function filterInboxTasksForDisplay(
  inboxTasks: Array<InboxTask>,
  entriesByRefId: { [key: string]: InboxTaskParent },
  optimisticUpdates: { [key: string]: InboxTaskOptimisticState },
  options: InboxTaskFilterOptions,
): Array<InboxTask> {
  return inboxTasks.filter((inboxTask) => {
    if (!options.allowArchived && inboxTask.archived) {
      return false;
    }

    if (options.allowSources !== undefined) {
      if (!options.allowSources.includes(inboxTask.source)) {
        return false;
      }
    }

    if (options.allowProjects !== undefined) {
      if (!options.allowProjects.includes(inboxTask.project_ref_id)) {
        return false;
      }
    }

    if (options.allowStatuses !== undefined) {
      if (inboxTask.ref_id in optimisticUpdates) {
        if (
          !options.allowStatuses.includes(
            optimisticUpdates[inboxTask.ref_id].status,
          )
        ) {
          return false;
        }
      } else if (!options.allowStatuses.includes(inboxTask.status)) {
        return false;
      }
    }

    if (options.allowEisens !== undefined) {
      if (
        inboxTask.ref_id in optimisticUpdates &&
        optimisticUpdates[inboxTask.ref_id].eisen !== undefined
      ) {
        if (
          !options.allowEisens.includes(
            optimisticUpdates[inboxTask.ref_id].eisen as Eisen,
          )
        ) {
          return false;
        }
      } else if (!options.allowEisens.includes(inboxTask.eisen)) {
        return false;
      }
    }

    if (options.allowDifficulties !== undefined) {
      if (inboxTask.difficulty !== undefined && inboxTask.difficulty !== null) {
        if (!options.allowDifficulties.includes(inboxTask.difficulty)) {
          return false;
        }
      }
    }

    if (!options.includeIfNoActionableDate && !inboxTask.actionable_date) {
      return false;
    }

    if (options.actionableDateStart !== undefined) {
      if (
        inboxTask.actionable_date &&
        aDateToDate(inboxTask.actionable_date) < options.actionableDateStart
      ) {
        return false;
      }
    }

    if (options.actionableDateEnd !== undefined) {
      if (
        inboxTask.actionable_date &&
        aDateToDate(inboxTask.actionable_date) > options.actionableDateEnd
      ) {
        return false;
      }
    }

    if (!options.includeIfNoDueDate && !inboxTask.due_date) {
      return false;
    }

    if (options.dueDateStart !== undefined) {
      if (
        inboxTask.due_date &&
        aDateToDate(inboxTask.due_date) < options.dueDateStart
      ) {
        return false;
      }
    }

    if (options.dueDateEnd !== undefined) {
      if (
        inboxTask.due_date &&
        aDateToDate(inboxTask.due_date) >= options.dueDateEnd
      ) {
        return false;
      }
    }

    if (options.allowPeriodsIfHabit) {
      const entry = entriesByRefId[inboxTask.ref_id];
      const habit = entry.habit as Habit;
      if (!options.allowPeriodsIfHabit.includes(habit.gen_params.period)) {
        return false;
      }
    }

    if (options.allowPeriodsIfChore) {
      const entry = entriesByRefId[inboxTask.ref_id];
      const chore = entry.chore as Chore;
      if (!options.allowPeriodsIfChore.includes(chore.gen_params.period)) {
        return false;
      }
    }

    return true;
  });
}

interface InboxTaskSortOptions {
  dueDateAscending?: boolean;
}

export function sortInboxTasksNaturally(
  inboxTasks: Array<InboxTask>,
  options?: InboxTaskSortOptions,
): Array<InboxTask> {
  let cleanOptions: InboxTaskSortOptions = {
    dueDateAscending: true,
  };
  if (options !== undefined) {
    cleanOptions = options;
  }

  return [...inboxTasks].sort((i1, i2) => {
    if (i2.archived && !i1.archived) {
      return -1;
    }

    if (i1.archived && !i2.archived) {
      return 1;
    }

    return (
      (cleanOptions.dueDateAscending ? 1 : -1) *
        compareADate(i1.due_date, i2.due_date) ||
      -1 * compareEisen(i1.eisen, i2.eisen) ||
      -1 *
        compareDifficulty(
          i1.difficulty ?? Difficulty.EASY,
          i2.difficulty ?? Difficulty.EASY,
        )
    );
  });
}

export function sortInboxTasksByEisenAndDifficulty(
  inboxTasks: Array<InboxTask>,
  options?: InboxTaskSortOptions,
): Array<InboxTask> {
  let cleanOptions: InboxTaskSortOptions = {
    dueDateAscending: true,
  };
  if (options !== undefined) {
    cleanOptions = options;
  }

  return [...inboxTasks].sort((i1, i2) => {
    return (
      -1 * compareEisen(i1.eisen, i2.eisen) ||
      -1 *
        compareDifficulty(
          i1.difficulty ?? Difficulty.EASY,
          i2.difficulty ?? Difficulty.EASY,
        ) ||
      (cleanOptions.dueDateAscending ? 1 : -1) *
        compareADate(i1.due_date, i2.due_date)
    );
  });
}

export function isInboxTaskCoreFieldEditable(source: InboxTaskSource): boolean {
  return source === InboxTaskSource.USER || source === InboxTaskSource.BIG_PLAN;
}

export function canInboxTaskBeInStatus(
  inboxTasks: InboxTask,
  status: InboxTaskStatus,
): boolean {
  switch (inboxTasks.source) {
    case InboxTaskSource.USER:
    case InboxTaskSource.BIG_PLAN:
      if (status === InboxTaskStatus.NOT_STARTED_GEN) {
        return false;
      }

      return true;
    case InboxTaskSource.WORKING_MEM_CLEANUP:
    case InboxTaskSource.HABIT:
    case InboxTaskSource.CHORE:
    case InboxTaskSource.JOURNAL:
    case InboxTaskSource.METRIC:
    case InboxTaskSource.PERSON_BIRTHDAY:
    case InboxTaskSource.PERSON_CATCH_UP:
    case InboxTaskSource.SLACK_TASK:
    case InboxTaskSource.EMAIL_TASK:
      if (status === InboxTaskStatus.NOT_STARTED) {
        return false;
      }

      return true;
  }
}

export function doesInboxTaskAllowChangingProject(
  source: InboxTaskSource,
): boolean {
  return source === InboxTaskSource.USER || source === InboxTaskSource.BIG_PLAN;
}

export function doesInboxTaskAllowChangingBigPlan(
  source: InboxTaskSource,
): boolean {
  return source === InboxTaskSource.USER || source === InboxTaskSource.BIG_PLAN;
}
