import { ApiError } from "@jupiter/webapi-client";
import { Card, CardContent, FormControl } from "@mui/material";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { DocEditor } from "~/components/doc-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = z.object({});

const CreateFormSchema = z.object({
  name: z.string(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.docs.docCreate({
      name: form.name,
      content: [],
    });

    return redirect(`/app/workspace/docs/${result.new_note.ref_id}`);
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
  const navigation = useNavigation();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={"docs/new"}
      returnLocation="/app/workspace/docs"
      inputsEnabled={inputsEnabled}
      initialExpansionState={LeafPanelExpansionState.FULL}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <FormControl fullWidth>
            <DocEditor inputsEnabled={inputsEnabled} />
          </FormControl>
        </CardContent>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/docs",
  ParamsSchema,
  {
    notFound: () => `Could not find the document!`,
    error: () => `There was an error creating the document! Please try again!`,
  },
);
