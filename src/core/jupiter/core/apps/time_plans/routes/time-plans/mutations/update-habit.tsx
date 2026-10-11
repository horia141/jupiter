import {
  Difficulty,
  Eisen,
  HabitRepeatsStrategy,
} from "@jupiter/webapi-client";
import type { ActionFunctionArgs } from "react-router";
import { z } from "zod";
import { CheckboxAsString, parseForm } from "zodix";

import { noErrorSomeData } from "#/core/infra/action-result";
import { handleActionApiError } from "#/core/infra/errors.server";
import {
  SchedulingParamsFormFields,
  schedulingParamsUpdateArgs,
} from "#/core/common/scheduling-params-form";
import { getLoggedInApiClient } from "#/core/infra/api-clients.server";

// Saves a habit as edited from the time plan view, and returns it for the view
// to merge in. Its period can't change, and its inbox tasks catch up on the
// next regen or gen.
const UpdateHabitFormSchema = z.object({
  refId: z.string(),
  name: z.string(),
  // Only sent when the workspace has a life plan.
  aspect: z.string().optional(),
  chapter: z.string().optional(),
  goal: z.string().optional(),
  stack: z.string().optional(),
  isKey: CheckboxAsString,
  eisen: z.nativeEnum(Eisen),
  difficulty: z.nativeEnum(Difficulty),
  actionableFromDay: z.string().optional(),
  actionableFromMonth: z.string().optional(),
  dueAtDay: z.string().optional(),
  dueAtMonth: z.string().optional(),
  skipRule: z.string().optional(),
  repeatsStrategy: z
    .nativeEnum(HabitRepeatsStrategy)
    .or(z.literal("none"))
    .optional(),
  repeatsInPeriodCount: z.string().optional(),
  suspended: CheckboxAsString,
  ...SchedulingParamsFormFields,
});

function intOrNull(value: string | undefined): number | null {
  return value ? parseInt(value, 10) : null;
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateHabitFormSchema);

  try {
    const result = await apiClient.habits.habitUpdate({
      ref_id: form.refId,
      name: { should_change: true, value: form.name },
      aspect_ref_id: form.aspect
        ? { should_change: true, value: form.aspect }
        : { should_change: false },
      chapter_ref_id: form.aspect
        ? { should_change: true, value: form.chapter || null }
        : { should_change: false },
      goal_ref_id: form.aspect
        ? { should_change: true, value: form.goal || null }
        : { should_change: false },
      stack_ref_id: { should_change: true, value: form.stack || null },
      is_key: { should_change: true, value: form.isKey },
      suspended: { should_change: true, value: form.suspended },
      eisen: { should_change: true, value: form.eisen },
      difficulty: { should_change: true, value: form.difficulty },
      actionable_from_day: {
        should_change: true,
        value: intOrNull(form.actionableFromDay),
      },
      actionable_from_month: {
        should_change: true,
        value: intOrNull(form.actionableFromMonth),
      },
      due_at_day: { should_change: true, value: intOrNull(form.dueAtDay) },
      due_at_month: { should_change: true, value: intOrNull(form.dueAtMonth) },
      skip_rule: { should_change: true, value: form.skipRule || null },
      repeats_strategy: {
        should_change: true,
        value:
          form.repeatsStrategy && form.repeatsStrategy !== "none"
            ? form.repeatsStrategy
            : null,
      },
      repeats_in_period_count: {
        should_change: true,
        value: intOrNull(form.repeatsInPeriodCount),
      },
      ...schedulingParamsUpdateArgs(form),
    });

    return noErrorSomeData({ updated_habit: result.updated_habit });
  } catch (error) {
    return handleActionApiError(error);
  }
}
