import { ApiError } from "@jupiter/webapi-client";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { NoteContentParser } from "~/logic/domain/notes";

const UpdateFormSchema = {
  docId: z.string(),
  noteId: z.string(),
  name: z.string(),
  content: z.preprocess((value) => {
    const utf8Buffer = Buffer.from(String(value), "base64");
    return JSON.parse(utf8Buffer.toString("utf-8"));
  }, NoteContentParser),
};

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    await apiClient.docs.docUpdate({
      ref_id: form.docId,
      name: { should_change: true, value: form.name },
    });
    await apiClient.notes.noteUpdate({
      ref_id: form.noteId,
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
