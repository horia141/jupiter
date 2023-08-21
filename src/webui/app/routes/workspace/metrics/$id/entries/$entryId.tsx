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
import { json, redirect } from "@remix-run/node";
import { ShouldRevalidateFunction, useActionData, useParams, useTransition } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { TimeDiffTag } from "~/components/time-diff-tag";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { aDateToDate } from "~/logic/domain/adate";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
  entryId: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
  collectionTime: z.string(),
  value: z.string().transform(parseFloat),
  notes: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { entryId } = parseParams(params, ParamsSchema);

  try {
    const result = await getLoggedInApiClient(session).metric.loadMetricEntry({
      ref_id: { the_id: entryId },
      allow_archived: true,
    });

    return json({
      metricEntry: result.metric_entry,
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
  const { id, entryId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(session).metric.updateMetricEntry({
          ref_id: { the_id: entryId },
          collection_time: {
            should_change: true,
            value: { the_date: form.collectionTime, the_datetime: undefined },
          },
          value: {
            should_change: true,
            value: form.value,
          },
          notes: {
            should_change: true,
            value: form.notes && form.notes !== "" ? form.notes : undefined,
          },
        });

        return redirect(`/workspace/metrics/${id}/entries/${entryId}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).metric.archiveMetricEntry({
          ref_id: { the_id: id },
        });

        return redirect(`/workspace/metrics/${id}/entries/${entryId}`);
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

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function MetricEntry() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.metricEntry.archived;

  return (
    <LeafCard
      key={loaderData.metricEntry.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/metrics/${id}`}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <TimeDiffTag
              labelPrefix="Collected"
              collectionTime={loaderData.metricEntry.collection_time}
            />
            <FormControl fullWidth>
              <InputLabel id="collectionTime">Collection Time</InputLabel>
              <OutlinedInput
                type="date"
                label="collectionTime"
                defaultValue={
                  loaderData.metricEntry.collection_time
                    ? aDateToDate(
                        loaderData.metricEntry.collection_time
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

            <FormControl fullWidth>
              <InputLabel id="notes">Notes</InputLabel>
              <OutlinedInput
                multiline
                minRows={2}
                maxRows={4}
                label="Notes"
                name="notes"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.metricEntry.notes}
              />
              <FieldError actionResult={actionData} fieldName="/notes" />
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
    </LeafCard>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () =>
    `Could not find metric entry #${useParams().id}:#${useParams().entryId}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading metric entry #${useParams().id}:#${
      useParams().entryId
    }! Please try again!`
);
