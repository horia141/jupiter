import type { ActionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { StatusCodes } from "http-status-codes";
import { ApiError, Eisen, InboxTaskStatus } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { getSession } from "~/sessions";

const UpdateStatusAndEisenFormSchema = {
  id: z.string(),
  status: z.nativeEnum(InboxTaskStatus),
  eisen: z.nativeEnum(Eisen).optional(),
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateStatusAndEisenFormSchema);

  try {
    await getLoggedInApiClient(session).inboxTask.updateInboxTask({
      ref_id: { the_id: form.id },
      name: { should_change: false },
      status: { should_change: true, value: form.status },
      eisen: form.eisen
        ? { should_change: true, value: form.eisen }
        : { should_change: false },
      difficulty: { should_change: false },
      actionable_date: { should_change: false },
      due_date: { should_change: false },
    });

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