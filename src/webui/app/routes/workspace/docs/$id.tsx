import { ApiError } from "@jupiter/webapi-client";
import { Card, CardContent, FormControl } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { DocEditor } from "~/components/doc-editor";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { LeafPanelExpansionState } from "~/rendering/leaf-panel-expansion";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({ intent: z.literal("archive") }),
  z.object({ intent: z.literal("remove") }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  try {
    const result = await apiClient.docs.docLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      doc: result.doc,
      note: result.note,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.NOT_FOUND) {
      throw new Response(ReasonPhrases.NOT_FOUND, {
        status: StatusCodes.NOT_FOUND,
        statusText: ReasonPhrases.NOT_FOUND,
      });
    }

    throw error;
  }
}

export async function action({ request, params }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "archive": {
        await apiClient.docs.docArchive({
          ref_id: id,
        });
        return redirect(`/workspace/docs`);
      }

      case "remove": {
        await apiClient.docs.docRemove({
          ref_id: id,
        });
        return redirect(`/workspace/docs`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
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

export default function Doc() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle" && !loaderData.doc.archived;

  return (
    <LeafPanel
      key={`doc-${loaderData.doc.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.doc.archived}
      returnLocation="/workspace/docs"
      initialExpansionState={LeafPanelExpansionState.FULL}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <FormControl fullWidth>
            <DocEditor
              initialDoc={loaderData.doc}
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </FormControl>
        </CardContent>
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find doc #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading doc #${useParams().id}. Please try again!`
);
