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
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/entity-note-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TimeDiffTag } from "~/components/time-diff-tag";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
  entryId: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    collectionTime: z.string(),
    value: z.string().transform(parseFloat),
  }),
  z.object({
    intent: z.literal("create-note"),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { entryId } = parseParams(params, ParamsSchema);

  try {
    const result = await apiClient.entry.metricEntryLoad({
      ref_id: entryId,
      allow_archived: true,
    });

    return json({
      metricEntry: result.metric_entry,
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id, entryId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.entry.metricEntryUpdate({
          ref_id: entryId,
          collection_time: {
            should_change: true,
            value: form.collectionTime,
          },
          value: {
            should_change: true,
            value: form.value,
          },
        });

        return redirect(`/app/workspace/metrics/${id}`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.METRIC_ENTRY,
          source_entity_ref_id: entryId,
          content: [],
        });

        return redirect(`/app/workspace/metrics/${id}/entries/${entryId}`);
      }

      case "archive": {
        await apiClient.entry.metricEntryArchive({
          ref_id: entryId,
        });

        return redirect(`/app/workspace/metrics/${id}`);
      }

      case "remove": {
        await apiClient.entry.metricEntryRemove({
          ref_id: entryId,
        });

        return redirect(`/app/workspace/metrics/${id}`);
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

export default function MetricEntry() {
  const { id, entryId } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.metricEntry.archived;

  const today = DateTime.local({ zone: topLevelInfo.user.timezone });

  return (
    <LeafPanel
      key={`metric-${id}/entry-${entryId}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.metricEntry.archived}
      returnLocation={`/app/workspace/metrics/${id}`}
    >
      <Card sx={{ marginBottom: "1rem" }}>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <TimeDiffTag
              today={today}
              labelPrefix="Collected"
              collectionTime={loaderData.metricEntry.collection_time}
            />
            <FormControl fullWidth>
              <InputLabel id="collectionTime" shrink>
                Collection Time
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="collectionTime"
                defaultValue={
                  loaderData.metricEntry.collection_time
                    ? aDateToDate(
                        loaderData.metricEntry.collection_time,
                      ).toFormat("yyyy-MM-dd")
                    : undefined
                }
                name="collectionTime"
                readOnly={!inputsEnabled}
              />

              <FieldError
                actionResult={actionData}
                fieldName="/collection_time"
              />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="value">Value</InputLabel>
              <OutlinedInput
                type="number"
                inputProps={{ step: "any" }}
                label="Value"
                name="value"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.metricEntry.value}
              />
              <FieldError actionResult={actionData} fieldName="/value" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
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
        {!loaderData.note && (
          <CardActions>
            <ButtonGroup>
              <Button
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

        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/metrics",
  ParamsSchema,
  {
    notFound: (params) =>
      `Could not find entry ${params.entryId} in metric ${params.id}!`,
    error: (params) =>
      `There was an error loading entry ${params.entryId} in metric ${params.id}! Please try again!`,
  },
);
