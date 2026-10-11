/**
 * Telling when a habit or chore edit changes what gets generated.
 *
 * Saving a habit or chore leaves its inbox tasks alone; they catch up on the
 * next regen or the hourly gen. When an edit changes how tasks are generated,
 * the view offers to regen right away.
 */
import type {
  Chore,
  Habit,
  RecurringTaskGenParams,
} from "@jupiter/webapi-client";

import type { RecurringTaskGenParamsEdit } from "#/core/apps/time_plans/store/mutations/form";
import type { UpdateChoreArgs } from "#/core/apps/time_plans/store/mutations/update-chore";
import type { UpdateHabitArgs } from "#/core/apps/time_plans/store/mutations/update-habit";

export const REGEN_HABIT_ACTION =
  "/app/workspace/apps/time-plans/mutations/regen-habit";
export const REGEN_CHORE_ACTION =
  "/app/workspace/apps/time-plans/mutations/regen-chore";

function orNull<T>(value: T | null | undefined): T | null {
  return value ?? null;
}

function genParamsChanged(
  current: RecurringTaskGenParams,
  edit: RecurringTaskGenParamsEdit,
): boolean {
  return (
    current.eisen !== edit.eisen ||
    current.difficulty !== edit.difficulty ||
    orNull(current.actionable_from_day) !== edit.actionableFromDay ||
    orNull(current.actionable_from_month) !== edit.actionableFromMonth ||
    orNull(current.due_at_day) !== edit.dueAtDay ||
    orNull(current.due_at_month) !== edit.dueAtMonth ||
    orNull(current.skip_rule) !== edit.skipRule
  );
}

/** Whether saving ``args`` over ``habit`` changes the tasks it generates. */
export function habitEditChangesGeneration(
  habit: Habit,
  args: UpdateHabitArgs,
): boolean {
  return (
    genParamsChanged(habit.gen_params, args.genParams) ||
    habit.suspended !== args.suspended ||
    orNull(habit.repeats_strategy) !== args.repeatsStrategy ||
    orNull(habit.repeats_in_period_count) !== args.repeatsInPeriodCount
  );
}

/** Whether saving ``args`` over ``chore`` changes the tasks it generates. */
export function choreEditChangesGeneration(
  chore: Chore,
  args: UpdateChoreArgs,
): boolean {
  return (
    genParamsChanged(chore.gen_params, args.genParams) ||
    chore.must_do !== args.mustDo ||
    chore.suspended !== args.suspended ||
    (args.startAtDate !== null && chore.start_at_date !== args.startAtDate) ||
    orNull(chore.end_at_date) !== args.endAtDate
  );
}
