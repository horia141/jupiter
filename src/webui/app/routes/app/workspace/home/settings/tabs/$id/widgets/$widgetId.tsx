import {
  ApiError,
} from "@jupiter/webapi-client";
import {
  FormControl,
  InputLabel,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { GlobalError } from "~/components/infra/errors";
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
import { WidgetTypeSelector } from "~/components/home/widget-type-selector";
import { WidgetDimensionSelector } from "~/components/home/widget-dimension-selector";
import { RowAndColSelector } from "~/components/home/row-and-col-selector";

const ParamsSchema = z.object({
  id: z.string(),
  widgetId: z.string(),
});

const QuerySchema = z.object({
  row: z.coerce.number(),
  col: z.coerce.number(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
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
  const { id, widgetId } = parseParams(params, ParamsSchema);

  const homeConfig = await apiClient.home.homeConfigLoad({});

  const tab = await apiClient.tab.homeTabLoad({
    ref_id: id,
    allow_archived: false,
  });

  const widget = await apiClient.widget.homeWidgetLoad({
    ref_id: widgetId,
    allow_archived: true,
  });

  return json({
    widget: widget.widget,
    widgetConstraints: homeConfig.widget_constraints,
    tab: tab.tab,
  });
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id, widgetId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);
  const query = await parseQuery(request, QuerySchema);

  try {
    switch (form.intent) {
      case "update":
        await apiClient.widget.homeWidgetMoveAndResize({
          ref_id: widgetId,
          row: query.row,
          col: query.col,
        });

        return redirect(
          `/app/workspace/home/settings/tabs/${id}`,
        );

      case "archive":
        await apiClient.widget.homeWidgetArchive({
          ref_id: widgetId,
        });
        return redirect(
          `/app/workspace/home/settings/tabs/${id}`,
        );

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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

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
      showArchiveAndRemoveButton
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
            <WidgetTypeSelector
              name="type"
              inputsEnabled={false}
              defaultValue={loaderData.widget.the_type}
              target={loaderData.tab.target}
              widgetConstraints={loaderData.widgetConstraints}
            />
          </FormControl>

          <FormControl fullWidth disabled>
            <RowAndColSelector
              row={loaderData.widget.geometry.row}
              col={loaderData.widget.geometry.col}
              target={loaderData.tab.target}
              inputsEnabled={false}
            />
          </FormControl>

          <FormControl fullWidth disabled>
            <InputLabel id="dimension">Dimension</InputLabel>
            <WidgetDimensionSelector
              name="dimension"
              inputsEnabled={false}
              defaultValue={loaderData.widget.geometry.dimension}
              target={loaderData.tab.target}
              widgetType={loaderData.widget.the_type}
              widgetConstraints={loaderData.widgetConstraints}
            />
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
