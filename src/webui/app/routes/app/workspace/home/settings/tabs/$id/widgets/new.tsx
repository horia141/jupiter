import { ApiError, HomeTabTarget, WidgetDimension, WidgetType } from "@jupiter/webapi-client";
import { FormControl, InputLabel, MenuItem, OutlinedInput, Select, Stack } from "@mui/material";
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
   row: z.coerce.number(),
   col: z.coerce.number(),
});

const CreateFormSchema = z.object({
  type: z.nativeEnum(WidgetType),
  dimension: z.nativeEnum(WidgetDimension),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);
  const query = await parseQuery(request, QuerySchema);

  try {
    const result = await apiClient.widget.homeWidgetCreate({
      home_tab_ref_id: id,
      the_type: form.type,
      row: query.row,
      col: query.col,
      dimension: form.dimension,
    });

    return redirect(`/app/workspace/home/settings/tabs/${params.id}/widgets/${result.new_widget.ref_id}`);
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
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={`home/settings/tabs/${id}/widgets/new`}
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
            <Select
              labelId="type"
              name="type"
              defaultValue={WidgetType.MOTD}
              disabled={!inputsEnabled}
            >
              {Object.values(WidgetType).map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
            <FieldError actionResult={actionData} fieldName="/type" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="dimension">Dimension</InputLabel>
            <Select
              labelId="dimension" 
              name="dimension"
              defaultValue={WidgetDimension.DIM_1X1}
              disabled={!inputsEnabled}
            >
              {Object.values(WidgetDimension).map((dim) => (
                <MenuItem key={dim} value={dim}>
                  {dim}
                </MenuItem>
              ))}
            </Select>
            <FieldError actionResult={actionData} fieldName="/dimension" />
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
