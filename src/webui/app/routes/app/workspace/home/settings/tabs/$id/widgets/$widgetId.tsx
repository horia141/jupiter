import { ApiError, HomeTabTarget, WidgetDimension, WidgetType } from "@jupiter/webapi-client";
import { FormControl, InputLabel, MenuItem, OutlinedInput, Select, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
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
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { SectionCardNew } from "~/components/infra/section-card-new";
const ParamsSchema = z.object({
  id: z.string(),
  widgetId: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
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
  const { widgetId } = parseParams(params, ParamsSchema);

  const widget = await apiClient.widget.homeWidgetLoad({
    ref_id: widgetId,
    allow_archived: true,
  });

  return json({ widget: widget.widget });
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id, widgetId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "archive":
        await apiClient.widget.homeWidgetArchive({
          ref_id: widgetId,
        });
        return redirect(`/app/workspace/home/settings/tabs/${id}/widgets/${widgetId}`);

      case "remove":
        await apiClient.widget.homeWidgetRemove({
          ref_id: widgetId,
        });
        return redirect(`/app/workspace/home/settings/tabs/${id}`);

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

export default function Widget() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={`home/settings/tabs/${id}/widgets/${loaderData.widget.ref_id}`}
      returnLocation={`/app/workspace/home/settings/tabs/${id}`}
      inputsEnabled={inputsEnabled}
    >
      <SectionCardNew
        title="Widget Settings"
        actions={
          <SectionActions
            id="widget-actions"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "widget-update",
                text: "Update",
                value: "update",
                disabled: !inputsEnabled,
                highlight: false,
              }),
            ]}
          />
        }
      >
        <GlobalError actionResult={actionData} />
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth disabled>
            <InputLabel id="type">Type</InputLabel>
            <Select
              labelId="type"
              value={loaderData.widget.the_type}
              disabled={!inputsEnabled}
            >
              <MenuItem value={loaderData.widget.the_type}>
                {loaderData.widget.the_type}
              </MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth disabled>
            <InputLabel id="dimension">Dimension</InputLabel>
            <Select
              labelId="dimension"
              value={loaderData.widget.geometry.dimension}
              disabled={!inputsEnabled}
            >
              <MenuItem value={loaderData.widget.geometry.dimension}>
                {loaderData.widget.geometry.dimension}
              </MenuItem>
            </Select>
          </FormControl>
        </Stack>
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/home/settings",
  ParamsSchema,
  {
    notFound: () => `Could not find the widget!`,
    error: () => `There was an error managing the widget! Please try again!`,
  },
);
