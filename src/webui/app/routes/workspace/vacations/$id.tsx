import { ApiError, NoteDomain } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect, Response } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
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
  startDate: z.string(),
  endDate: z.string(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const result = await getLoggedInApiClient(session).vacations.vacationLoad({
      ref_id: id,
      allow_archived: true,
    });

    return json({
      vacation: result.vacation,
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
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(session).vacations.vacationUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          start_date: {
            should_change: true,
            value: form.startDate,
          },
          end_date: {
            should_change: true,
            value: form.endDate,
          },
        });

        return redirect(`/workspace/vacations/${id}`);
      }

      case "create-note": {
        await getLoggedInApiClient(session).core.noteCreate({
          domain: NoteDomain.VACATION,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/workspace/vacations/${id}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).vacations.vacationArchive({
          ref_id: id,
        });
        return redirect(`/workspace/vacations/${id}`);
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

export default function Vacation() {
  const { vacation, note } = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle" && !vacation.archived;

  return (
    <LeafPanel
      key={`vacation-${vacation.ref_id}`}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation="/workspace/vacations"
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="name"
                name="name"
                readOnly={!inputsEnabled}
                defaultValue={vacation.name}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="startDate">Start Date</InputLabel>
              <OutlinedInput
                type="date"
                label="startDate"
                defaultValue={aDateToDate(vacation.start_date).toFormat(
                  "yyyy-MM-dd"
                )}
                name="startDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/start_date" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="endDate">End Date</InputLabel>
              <OutlinedInput
                type="date"
                label="endDate"
                defaultValue={aDateToDate(vacation.end_date).toFormat(
                  "yyyy-MM-dd"
                )}
                name="endDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/end_date" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="vacation-update"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      <Card>
        {!note && (
          <CardActions>
            <ButtonGroup>
              <Button
                id="vacation-create-note"
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
                name="intent"
                value="create-note"
              >
                Create Note
              </Button>
            </ButtonGroup>
          </CardActions>
        )}

        {note && (
          <>
            <EntityNoteEditor
              initialNote={note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find vacation #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading vacation #${useParams().id}. Please try again!`
);
