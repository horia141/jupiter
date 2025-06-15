import { ApiError, WidgetDimension, WidgetType } from "@jupiter/webapi-client";
import { FormControl, InputLabel, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useLoaderData,
  useNavigation,
  useParams,
  useSearchParams,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { parseForm, parseParams, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { WidgetDimensionSelector } from "~/components/home/widget-dimension-selector";
import { WidgetTypeSelector } from "~/components/home/widget-type-selector";
import { RowAndColSelector } from "~/components/home/row-and-col-selector";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
});

const QuerySchema = z.object({
  row: z.coerce.number().optional(),
  col: z.coerce.number().optional(),
});

const CreateFormSchema = z.object({
  type: z.nativeEnum(WidgetType),
  dimension: z.nativeEnum(WidgetDimension),
  widgetRow: z.coerce.number(),
  widgetCol: z.coerce.number(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const tab = await apiClient.tab.homeTabLoad({
    ref_id: id,
    allow_archived: false,
  });

  const homeConfig = await apiClient.home.homeConfigLoad({});
  return json({
    widgetConstraints: homeConfig.widget_constraints,
    tab: tab.tab,
    widgets: tab.widgets,
  });
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.widget.homeWidgetCreate({
      home_tab_ref_id: id,
      the_type: form.type,
      row: form.widgetRow,
      col: form.widgetCol,
      dimension: form.dimension,
    });

    return redirect(
      `/app/workspace/home/settings/tabs/${params.id}/widgets/${result.new_widget.ref_id}`,
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

export default function NewWidget() {
  const { id } = useParams();
  const loaderData = useLoaderData<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(parseQuery(searchParams, QuerySchema));

  const [theType, setTheType] = useState<WidgetType>(WidgetType.MOTD);

  useEffect(() => {
    setQuery(parseQuery(searchParams, QuerySchema));
  }, [searchParams]);

  return (
    <LeafPanel
      fakeKey={`home/settings/tabs/${id}/widgets/new`}
      returnLocation={`/app/workspace/home/settings/tabs/${id}`}
      inputsEnabled={inputsEnabled}
    >
      <SectionCardNew
        title="New Widget"
        actions={
          <SectionActions
            id="widget-create"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "widget-create",
                text: "Create",
                value: "create",
                disabled: !inputsEnabled,
                highlight: true,
              }),
            ]}
          />
        }
      >
        <GlobalError actionResult={actionData} />
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="type">Type</InputLabel>
            <WidgetTypeSelector
              user={topLevelInfo.user}
              workspace={topLevelInfo.workspace}
              name="type"
              inputsEnabled={inputsEnabled}
              value={theType}
              onChange={(type) => setTheType(type)}
              target={loaderData.tab.target}
              widgetConstraints={loaderData.widgetConstraints}
            />
            <FieldError actionResult={actionData} fieldName="/type" />
          </FormControl>

          <FormControl fullWidth disabled>
            <RowAndColSelector
              namePrefix="widget"
              target={loaderData.tab.target}
              homeTab={loaderData.tab}
              widgets={loaderData.widgets}
              row={query.row ?? 0}
              col={query.col ?? 0}
              inputsEnabled={inputsEnabled}
            />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="dimension">Dimension</InputLabel>
            <WidgetDimensionSelector
              name="dimension"
              inputsEnabled={inputsEnabled}
              defaultValue={
                loaderData.widgetConstraints[theType].allowed_dimensions[
                  loaderData.tab.target
                ][0]
              }
              target={loaderData.tab.target}
              widgetType={theType}
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
    notFound: () => `Could not find the tab!`,
    error: () => `There was an error creating the widget! Please try again!`,
  },
);
