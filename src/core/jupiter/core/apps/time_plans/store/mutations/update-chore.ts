/**
 * Saving a chore edited from the time plan view.
 *
 * Its inbox tasks aren't touched: they catch up on the next regen or gen.
 */
import type { ADate, Chore, ChoreUpdateResult } from "@jupiter/webapi-client";
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
  recurringTaskGenParamsFromForm,
  recurringTaskGenParamsPatch,
  recurringTaskGenParamsToFormFields,
  schedulingParamsFromForm,
  schedulingParamsPatch,
  schedulingParamsToFormFields,
} from "#/core/apps/time_plans/store/mutations/form";

export interface UpdateChoreArgs {
  refId: string;
  name: string;
  // Left alone when null.
  lifePlan: LifePlanAssociation | null;
  stackRefId: string | null;
  isKey: boolean;
  genParams: RecurringTaskGenParamsEdit;
  schedulingParams: SchedulingParamsEdit;
  mustDo: boolean;
  suspended: boolean;
  // A chore always has a start date, so none means leave it alone.
  startAtDate: ADate | null;
  endAtDate: ADate | null;
  // When the edit was made, standing in for the server's modification time
  // until the result arrives.
  modifiedTime: string;
}

const ChorePropertiesFormSchema = z.object({
  refId: z.string(),
  name: z.string(),
});

/** The args from a chore properties editor's form. */
export function updateChoreArgsFromForm(
  formData: FormData,
  modifiedTime: string,
  namePrefix: string,
): UpdateChoreArgs {
  const field = editorFormFields(formData, namePrefix);
  const form = ChorePropertiesFormSchema.parse({
    refId: field("refId"),
    name: field("name"),
  });

  return {
    refId: form.refId,
    name: form.name,
    lifePlan: lifePlanAssociationFromForm(field),
    stackRefId: field("stack") || null,
    isKey: field("isKey") === "on",
    genParams: recurringTaskGenParamsFromForm(field),
    schedulingParams: schedulingParamsFromForm(field),
    mustDo: field("mustDo") === "on",
    suspended: field("suspended") === "on",
    startAtDate: field("startAtDate") || null,
    endAtDate: field("endAtDate") || null,
    modifiedTime,
  };
}

export const UPDATE_CHORE: TimePlanMutation<
  UpdateChoreArgs,
  Pick<ChoreUpdateResult, "updated_chore">
> = {
  action: "/app/workspace/apps/time-plans/mutations/update-chore",
  toFormFields: (args) => ({
    refId: args.refId,
    name: args.name,
    ...lifePlanAssociationToFormFields(args.lifePlan),
    stack: args.stackRefId ?? "",
    ...(args.isKey ? { isKey: "on" } : {}),
    ...recurringTaskGenParamsToFormFields(args.genParams),
    ...schedulingParamsToFormFields(args.schedulingParams),
    ...(args.mustDo ? { mustDo: "on" } : {}),
    ...(args.suspended ? { suspended: "on" } : {}),
    startAtDate: args.startAtDate ?? "",
    endAtDate: args.endAtDate ?? "",
  }),
  applyOptimistic: (entities, args) => {
    const chore = entities.chores[args.refId];
    if (chore === undefined) {
      return entities;
    }
    const updated: Chore = {
      ...chore,
      ...lifePlanAssociationPatch(args.lifePlan),
      name: args.name,
      stack_ref_id: args.stackRefId,
      is_key: args.isKey,
      gen_params: recurringTaskGenParamsPatch(chore.gen_params, args.genParams),
      scheduling_params: schedulingParamsPatch(args.schedulingParams),
      must_do: args.mustDo,
      suspended: args.suspended,
      start_at_date: args.startAtDate ?? chore.start_at_date,
      end_at_date: args.endAtDate,
      last_modified_time: args.modifiedTime,
    };
    return {
      ...entities,
      chores: { ...entities.chores, [args.refId]: updated },
    };
  },
  toDelta: (result) => ({ chores: [result.updated_chore] }),
};
