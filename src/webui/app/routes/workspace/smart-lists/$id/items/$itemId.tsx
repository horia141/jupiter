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
import {
  ShouldRevalidateFunction,
  useActionData,
  useParams,
  useTransition,
} from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TagsEditor } from "~/components/tags-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
  itemId: z.string(),
};

const UpdateFormSchema = {
  intent: z.string(),
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
  const { itemId } = parseParams(params, ParamsSchema);

  try {
    const result = await getLoggedInApiClient(
      session
    ).smartLists.smartListItemLoad({
      ref_id: itemId,
      allow_archived: true,
    });

    return json({
      smartListItem: result.smart_list_item,
      smartListTags: result.smart_list_tags,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.NOT_FOUND) {
      throw new Response(ReasonPhrases.NOT_FOUND, {
        status: StatusCodes.NOT_FOUND,
        statusText: ReasonPhrases.NOT_FOUND,
      });
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export async function action({ request, params }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id, itemId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await getLoggedInApiClient(session).smartLists.smartListItemUpdate({
          ref_id: itemId,
          name: {
            should_change: true,
            value: form.name,
          },
          is_done: {
            should_change: true,
            value: form.isDone,
          },
          tags: {
            should_change: true,
            value: form.tags,
          },
          url: {
            should_change: true,
            value: form.url,
          },
        });

        return redirect(`/workspace/smart-lists/${id}/items/${itemId}`);
      }

      case "archive": {
        await getLoggedInApiClient(session).smartLists.smartListItemArchive({
          ref_id: itemId,
        });

        return redirect(`/workspace/smart-lists/${id}/items/${itemId}`);
      }
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

export default function SmartListItem() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled =
    transition.state === "idle" && !loaderData.smartListItem.archived;

  return (
    <LeafPanel
      key={loaderData.smartListItem.ref_id}
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
                defaultValue={loaderData.smartListItem.name}
                name="name"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <FormControlLabel
                control={
                  <Switch
                    name="isDone"
                    readOnly={!inputsEnabled}
                    disabled={!inputsEnabled}
                    defaultChecked={loaderData.smartListItem.is_done}
                  />
                }
                label="Is Done"
              />
              <FieldError actionResult={actionData} fieldName="/is_done" />
            </FormControl>

            <FormControl fullWidth>
              <TagsEditor
                allTags={loaderData.smartListTags}
                defaultTags={loaderData.smartListItem.tags_ref_id}
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/tags" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="url">Url</InputLabel>
              <OutlinedInput
                label="Url"
                name="url"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.smartListItem.url?.the_url}
              />
              <FieldError actionResult={actionData} fieldName="/url" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Save
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const CatchBoundary = makeCatchBoundary(
  () =>
    `Could not find smart list item #${useParams().id}:#${useParams().itemId}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading smart list item #${useParams().id}:#${
      useParams().itemId
    }! Please try again!`
);
