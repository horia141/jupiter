import { ApiError, Eisen, InboxTaskStatus } from "@jupiter/webapi-client";
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

const UpdateStatusAndEisenFormSchema = {
  id: z.string(),
  status: z.nativeEnum(InboxTaskStatus),
  eisen: z.nativeEnum(Eisen).or(z.literal("no-go")).optional(),
};

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateStatusAndEisenFormSchema);

  try {
    const result = await apiClient.inboxTasks.inboxTaskUpdate({
      ref_id: form.id,
      name: { should_change: false },
      status: { should_change: true, value: form.status },
      eisen:
        form.eisen !== "no-go" && form.eisen !== undefined
          ? { should_change: true, value: form.eisen }
          : { should_change: false },
      difficulty: { should_change: false },
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
