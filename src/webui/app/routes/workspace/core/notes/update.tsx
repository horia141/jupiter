import { ActionArgs, json } from "@remix-run/node";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { NoteContentParser } from "~/logic/domain/notes";
import { getSession } from "~/sessions";

const UpdateForEntityFormSchema = {
  id: z.string(),
  content: z.preprocess(
    (value) => JSON.parse(atob(String(value))),
    NoteContentParser
  ),
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateForEntityFormSchema);

  try {
    const result = await getLoggedInApiClient(session).core.noteUpdate({
      ref_id: form.id,
      content: { should_change: true, value: form.content },
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
