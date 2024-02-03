import { Card, CardContent, FormControl } from "@mui/material";
import type { ActionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  ShouldRevalidateFunction,
  useActionData,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { DocEditor } from "~/components/doc-editor";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const CreateFormSchema = {
  name: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await getLoggedInApiClient(session).docs.docCreate({
      name: { the_name: form.name },
      content: [],
    });

    return redirect(`/workspace/docs/${result.new_note.ref_id.the_id}`);
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function NewDoc() {
  const transition = useTransition();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel
      returnLocation="/workspace/docs"
      initialExpansionState={LeafPanelExpansionState.FULL}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <FormControl fullWidth>
            <DocEditor inputsEnabled={inputsEnabled} />
            <FieldError actionResult={actionData} fieldName="/name" />
            <FieldError actionResult={actionData} fieldName="/content" />
          </FormControl>
        </CardContent>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the note! Please try again!`
);
