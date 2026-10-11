/**
 * Saving a habit edited from the time plan view.
 *
 * Its inbox tasks aren't touched: they catch up on the next regen or gen.
 */
import type { Habit, HabitUpdateResult } from "@jupiter/webapi-client";
import { HabitRepeatsStrategy } from "@jupiter/webapi-client";
import { z } from "zod";

import type { TimePlanMutation } from "#/core/apps/time_plans/store/mutation";
import type {
  LifePlanAssociation,
  RecurringTaskGenParamsEdit,
  SchedulingParamsEdit,
} from "#/core/apps/time_plans/store/mutations/form";
import {
  editorFormFields,
  lifePlanAssociationFromForm,
  lifePlanAssociationPatch,
  lifePlanAssociationToFormFields,
  nullableIntFromForm,
  recurringTaskGenParamsFromForm,
  recurringTaskGenParamsPatch,
  recurringTaskGenParamsToFormFields,
  schedulingParamsFromForm,
  schedulingParamsPatch,
  schedulingParamsToFormFields,
} from "#/core/apps/time_plans/store/mutations/form";

export interface UpdateHabitArgs {
  refId: string;
  name: string;
  // Left alone when null.
  lifePlan: LifePlanAssociation | null;
  stackRefId: string | null;
  isKey: boolean;
  genParams: RecurringTaskGenParamsEdit;
  schedulingParams: SchedulingParamsEdit;
  repeatsStrategy: HabitRepeatsStrategy | null;
  repeatsInPeriodCount: number | null;
  suspended: boolean;
  // When the edit was made, standing in for the server's modification time
  // until the result arrives.
  modifiedTime: string;
}

const HabitPropertiesFormSchema = z.object({
  refId: z.string(),
  name: z.string(),
  repeatsStrategy: z.nativeEnum(HabitRepeatsStrategy).nullable(),
});

/** The args from a habit properties editor's form. */
export function updateHabitArgsFromForm(
  formData: FormData,
  modifiedTime: string,
  namePrefix: string,
): UpdateHabitArgs {
  const field = editorFormFields(formData, namePrefix);
  const repeatsStrategy = field("repeatsStrategy");
  const form = HabitPropertiesFormSchema.parse({
    refId: field("refId"),
    name: field("name"),
    repeatsStrategy:
      repeatsStrategy && repeatsStrategy !== "none" ? repeatsStrategy : null,
  });

  return {
    refId: form.refId,
    name: form.name,
    lifePlan: lifePlanAssociationFromForm(field),
    stackRefId: field("stack") || null,
    isKey: field("isKey") === "on",
    genParams: recurringTaskGenParamsFromForm(field),
    schedulingParams: schedulingParamsFromForm(field),
    repeatsStrategy: form.repeatsStrategy,
    repeatsInPeriodCount:
      form.repeatsStrategy === null
        ? null
        : nullableIntFromForm(field("repeatsInPeriodCount")),
    suspended: field("suspended") === "on",
    modifiedTime,
  };
}

export const UPDATE_HABIT: TimePlanMutation<
  UpdateHabitArgs,
  Pick<HabitUpdateResult, "updated_habit">
> = {
  action: "/app/workspace/apps/time-plans/mutations/update-habit",
  toFormFields: (args) => ({
    refId: args.refId,
    name: args.name,
    ...lifePlanAssociationToFormFields(args.lifePlan),
    stack: args.stackRefId ?? "",
    ...(args.isKey ? { isKey: "on" } : {}),
    ...recurringTaskGenParamsToFormFields(args.genParams),
    ...schedulingParamsToFormFields(args.schedulingParams),
    repeatsStrategy: args.repeatsStrategy ?? "none",
    repeatsInPeriodCount: args.repeatsInPeriodCount?.toString() ?? "",
    ...(args.suspended ? { suspended: "on" } : {}),
  }),
  applyOptimistic: (entities, args) => {
    const habit = entities.habits[args.refId];
    if (habit === undefined) {
      return entities;
    }
    const updated: Habit = {
      ...habit,
      ...lifePlanAssociationPatch(args.lifePlan),
      name: args.name,
      stack_ref_id: args.stackRefId,
      is_key: args.isKey,
      gen_params: recurringTaskGenParamsPatch(habit.gen_params, args.genParams),
      scheduling_params: schedulingParamsPatch(args.schedulingParams),
      repeats_strategy: args.repeatsStrategy,
      repeats_in_period_count: args.repeatsInPeriodCount,
      suspended: args.suspended,
      last_modified_time: args.modifiedTime,
    };
    return {
      ...entities,
      habits: { ...entities.habits, [args.refId]: updated },
    };
  },
  toDelta: (result) => ({ habits: [result.updated_habit] }),
};
