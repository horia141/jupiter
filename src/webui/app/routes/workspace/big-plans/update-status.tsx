import { ApiError, BigPlanStatus } from "@jupiter/webapi-client";
import type { ActionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { saveScoreAction } from "~/logic/domain/gamification/scores.server";

const UpdateStatusFormSchema = {
  id: z.string(),
  status: z.nativeEnum(BigPlanStatus),
};

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateStatusFormSchema);

  try {
    const result = await apiClient.bigPlans.bigPlanUpdate({
      ref_id: form.id,
      name: { should_change: false },
      status: { should_change: true, value: form.status },
      actionable_date: { should_change: false },
      due_date: { should_change: false },
    });

    if (result.record_score_result) {
      return json(noErrorNoData(), {
        headers: {
          "Set-Cookie": await saveScoreAction(result.record_score_result),
        },
      });
    }

    return json(noErrorNoData());
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body));
    }

    throw error;
  }
}
