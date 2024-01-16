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

const UpdateFormSchema = {
  docId: z.string(),
  noteId: z.string(),
  name: z.string(),
  content: z.preprocess(
    (value) => JSON.parse(atob(String(value))),
    NoteContentParser
  ),
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, UpdateFormSchema);

  try {
    await getLoggedInApiClient(session).doc.updateDoc({
      ref_id: { the_id: form.docId },
      name: { should_change: true, value: { the_name: form.name } },
    });
    await getLoggedInApiClient(session).note.updateNote({
      ref_id: { the_id: form.noteId },
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