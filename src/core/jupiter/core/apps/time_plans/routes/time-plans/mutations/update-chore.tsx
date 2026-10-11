import { Difficulty, Eisen } from "@jupiter/webapi-client";
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

// Saves a chore as edited from the time plan view, and returns it for the view
// to merge in. Its period can't change, and its inbox tasks catch up on the
// next regen or gen.
const UpdateChoreFormSchema = z.object({
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
  mustDo: CheckboxAsString,
  suspended: CheckboxAsString,
  startAtDate: z.string().optional(),
  endAtDate: z.string().optional(),
  ...SchedulingParamsFormFields,
});

function intOrNull(value: string | undefined): number | null {
  return value ? parseInt(value, 10) : null;
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateChoreFormSchema);

  try {
    const result = await apiClient.chores.choreUpdate({
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
      must_do: { should_change: true, value: form.mustDo },
      suspended: { should_change: true, value: form.suspended },
      skip_rule: { should_change: true, value: form.skipRule || null },
      // A chore always has a start date, so an empty one is left alone.
      start_at_date: form.startAtDate
        ? { should_change: true, value: form.startAtDate }
        : { should_change: false },
      end_at_date: { should_change: true, value: form.endAtDate || null },
      ...schedulingParamsUpdateArgs(form),
    });

    return noErrorSomeData({ updated_chore: result.updated_chore });
  } catch (error) {
    return handleActionApiError(error);
  }
}
