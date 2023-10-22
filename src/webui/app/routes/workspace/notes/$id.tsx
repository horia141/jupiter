import { Card, CardContent, FormControl } from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import {
  ShouldRevalidateFunction,
  useActionData,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { NoteEditor } from "~/components/note-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  name: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const result = await getLoggedInApiClient(session).note.loadNote({
      ref_id: { the_id: id },
      allow_archived: true,
    });

    return json(result.note);
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
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "archive": {
        await getLoggedInApiClient(session).note.archiveNote({
          ref_id: { the_id: id },
        });
        return redirect(`/workspace/notes/${id}`);
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

export default function Note() {
  const note = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle" && !note.archived;

  return (
    <LeafCard
      key={note.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/notes"
      startExpanded
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <FormControl fullWidth>
            <NoteEditor initialNote={note} inputsEnabled={inputsEnabled} />
            <FieldError actionResult={actionData} fieldName="/name" />
            <FieldError actionResult={actionData} fieldName="/content" />
          </FormControl>
        </CardContent>
      </Card>
    </LeafCard>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find note #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading note #${useParams().id}. Please try again!`
);
