import { ApiError } from "@jupiter/webapi-client";
import {
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Switch,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TagsEditor } from "~/components/domain/core/tags-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCard, ActionsPosition } from "~/components/infra/section-card";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
});

const CreateFormSchema = z.object({
  name: z.string(),
  isDone: CheckboxAsString,
  tags: z
    .string()
    .transform((s) => (s.trim() !== "" ? s.trim().split(",") : [])),
  url: z
    .string()
    .transform((s) => (s === "" ? undefined : s))
    .optional(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const result = await apiClient.smartLists.smartListLoad({
    ref_id: id,
    allow_archived: true,
    allow_archived_items: false,
    allow_archived_tags: false,
  });

  return json({
    smartList: result.smart_list,
    smartListTags: result.smart_list_tags,
  });
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const response = await apiClient.item.smartListItemCreate({
      smart_list_ref_id: id,
      name: form.name,
      is_done: form.isDone,
      tag_names: form.tags,
      url: form.url,
    });

    return redirect(
      `/app/workspace/smart-lists/${id}/items/${response.new_smart_list_item.ref_id}`,
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

export default function NewSmartListItem() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      fakeKey={`smart-list-${id}/items/new`}
      returnLocation={`/app/workspace/smart-lists/${id}/items`}
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="New Smart List Item"
        actionsPosition={ActionsPosition.BELOW}
        actions={
          <SectionActions
            id="smart-list-item-create"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "smart-list-item-create",
                text: "Create",
                value: "create",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <FormControl fullWidth>
          <InputLabel id="name">Name</InputLabel>
          <OutlinedInput
            label="Name"
            name="name"
            readOnly={!inputsEnabled}
            defaultValue={""}
          />

          <FieldError actionResult={actionData} fieldName="/name" />
        </FormControl>

        <FormControl fullWidth>
          <FormControlLabel
            control={<Switch name="isDone" readOnly={!inputsEnabled} />}
            label="Is Done"
          />
          <FieldError actionResult={actionData} fieldName="/is_done" />
        </FormControl>

        <FormControl fullWidth>
          <TagsEditor
            allTags={loaderData.smartListTags}
            defaultTags={[]}
            readOnly={!inputsEnabled}
          />
          <FieldError actionResult={actionData} fieldName="/tag_names" />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="url">Url [Optional]</InputLabel>
          <OutlinedInput label="Url" name="url" readOnly={!inputsEnabled} />
          <FieldError actionResult={actionData} fieldName="/url" />
        </FormControl>
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params) => `/app/workspace/smart-lists/${params.id}/items`,
  ParamsSchema,
  {
    notFound: () => `Could not find the smart list item!`,
    error: () =>
      `There was an error creating the smart list item! Please try again!`,
  },
);
