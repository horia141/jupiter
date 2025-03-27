import { ApiError } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  Switch,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useParams, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";

import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TagsEditor } from "~/components/tags-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = {
  id: z.string(),
};

const CreateFormSchema = {
  name: z.string(),
  isDone: CheckboxAsString,
  tags: z
    .string()
    .transform((s) => (s.trim() !== "" ? s.trim().split(",") : [])),
  url: z
    .string()
    .transform((s) => (s === "" ? undefined : s))
    .optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
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

export async function action({ request, params }: ActionArgs) {
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

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={`smart-list-${id}/items/new`}
      returnLocation={`/app/workspace/smart-lists/${id}/items`}
      inputsEnabled={inputsEnabled}
    >
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
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
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="smart-list-item-create"
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

export const ErrorBoundary = makeLeafErrorBoundary(
  () => `/app/workspace/smart-lists/${useParams().id}/items`,
  () => `There was an error creating the smart list item! Please try again!`,
);
