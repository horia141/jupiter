import { ApiError } from "@jupiter/webapi-client";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import {
  noErrorSomeData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { NoteContentParser } from "~/logic/domain/notes";

const CreateFormSchema = z.object({
  idempotencyKey: z.string(),
  name: z.string(),
  content: z.preprocess((value) => {
    const utf8Buffer = Buffer.from(String(value), "base64");
    return JSON.parse(utf8Buffer.toString("utf-8"));
  }, NoteContentParser),
});

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.docs.docCreate({
      idempotency_key: form.idempotencyKey,
      name: form.name,
      content: form.content,
    });

    return json(
      noErrorSomeData({ new_doc: result.new_doc, new_note: result.new_note }),
    );
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
