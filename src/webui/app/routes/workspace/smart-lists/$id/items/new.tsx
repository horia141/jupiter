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
import { useActionData, useParams, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafCard } from "~/components/infra/leaf-card";
import { TagsEditor } from "~/components/tags-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

const CreateFormSchema = {
  name: z.string(),
  isDone: CheckboxAsString,
  tags: z
    .string()
    .transform((s) => (s.trim() !== "" ? s.trim().split(",") : [])),
  url: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  const result = await getLoggedInApiClient(session).smartList.loadSmartList({
    allow_archived: true,
    ref_id: { the_id: id },
  });

  return json({
    smartList: result.smart_list,
    smartListTags: result.smart_list_tags,
  });
}

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).smartList.createSmartListItem({
      smart_list_ref_id: { the_id: id },
      name: { the_name: form.name },
      is_done: form.isDone,
      tag_names: form.tags.map((tag) => ({ the_tag: tag })),
      url: form.url ? { the_url: form.url } : undefined,
    });

    return redirect(
      `/workspace/smart-lists/${id}/items/${response.new_smart_list_item.ref_id.the_id}`
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

export default function NewSmartListItem() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafCard
      key={loaderData.smartList.ref_id.the_id}
      showArchiveButton
      enableArchiveButton={inputsEnabled}
      returnLocation={`/workspace/smart-lists/${id}/items`}
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
              <InputLabel id="url">Url</InputLabel>
              <OutlinedInput label="Url" name="url" readOnly={!inputsEnabled} />
              <FieldError actionResult={actionData} fieldName="/url" />
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
  () => `There was an error creating the smart list item! Please try again!`
);
