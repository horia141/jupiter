import { ApiError } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
});

const CreateFormSchema = z.object({
  collectionTime: z.string(),
  value: z.string().transform(parseFloat),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const response = await apiClient.metrics.metricLoad({
    ref_id: id,
    allow_archived: true,
    allow_archived_entries: false,
  });

  return json({
    metric: response.metric,
  });
}

export async function action({ params, request }: ActionFunctionArgs) {
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
      `/app/workspace/metrics/${id}/entries/${response.new_metric_entry.ref_id}`,
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
  const navigation = useNavigation();

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={`metric-${id}/entries/new`}
      fakeKey={`metric-${id}/entries/new`}
      returnLocation={`/app/workspace/metrics/${loaderData.metric.ref_id}`}
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="New Metric Entry"
        actionsPosition={ActionsPosition.BELOW}
        actions={
          <SectionActions
            id="metric-entry-create"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "metric-entry-create",
                text: "Create",
                value: "create",
                highlight: true,
              }),
            ]}
          />
        }
      >
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
            disabled={!inputsEnabled}
          />

          <FieldError actionResult={actionData} fieldName="/collection_time" />
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
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params) => `/app/workspace/metrics/${params.id}`,
  ParamsSchema,
  {
    error: () =>
      `There was an error creating the metric entry! Please try again!`,
  },
);
