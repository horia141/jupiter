import { ApiError } from "@jupiter/webapi-client";
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
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = {
  id: z.string(),
};

const CreateFormSchema = {
  collectionTime: z.string(),
  value: z.string().transform(parseFloat),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const response = await apiClient.metrics.metricLoad({
    allow_archived: true,
    ref_id: id,
  });

  return json({
    metric: response.metric,
  });
}

export async function action({ params, request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const response = await apiClient.entry.metricEntryCreate({
      metric_ref_id: id,
      collection_time: form.collectionTime,
      value: form.value,
    });

    return redirect(
      `/workspace/metrics/${id}/entries/${response.new_metric_entry.ref_id}`
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function NewMetricEntry() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel
      key={`metric-${id}/entries/new`}
      returnLocation={`/workspace/metrics/${loaderData.metric.ref_id}`}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="collectionTime" shrink>
                Collection Time
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="collectionTime"
                defaultValue={DateTime.local({
                  zone: topLevelInfo.user.timezone,
                }).toFormat("yyyy-MM-dd")}
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
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="metric-entry-create"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
            >
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the metric entry! Please try again!`
);
