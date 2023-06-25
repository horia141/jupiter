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
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { DateTime } from "luxon";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

const CreateFormSchema = {
  collectionTime: z.string(),
  value: z.string().transform(parseFloat),
  notes: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  const response = await getLoggedInApiClient(session).metric.loadMetric({
    allow_archived: true,
    ref_id: { the_id: id },
  });

  return json({
    metric: response.metric,
  });
}

export async function action({ params, request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).metric.createMetricEntry({
      metric_ref_id: { the_id: id },
      collection_time: {
        the_date: form.collectionTime,
        the_datetime: undefined,
      },
      value: form.value,
      notes: form.notes && form.notes !== "" ? form.notes : undefined,
    });

    return redirect(
      `/workspace/metrics/${id}/entries/${response.new_metric_entry.ref_id.the_id}`
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

export default function NewMetricEntry() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafCard
      key={loaderData.metric.ref_id.the_id}
      returnLocation={`/workspace/metrics/${loaderData.metric.ref_id.the_id}`}
    >
      <GlobalError actionResult={actionData} />
      <Card>
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="collectionTime">Collection Time</InputLabel>
              <OutlinedInput
                type="date"
                label="collectionTime"
                defaultValue={DateTime.now().toFormat("yyyy-MM-dd")}
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
              />
              <FieldError actionResult={actionData} fieldName="/notes" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the metric entry! Please try again!`
);
