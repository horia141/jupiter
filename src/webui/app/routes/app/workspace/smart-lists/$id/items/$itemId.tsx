import { ApiError, NoteDomain } from "@jupiter/webapi-client";
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
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { CheckboxAsString, parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/infra/entity-note-editor";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { TagsEditor } from "~/components/domain/core/tags-editor";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { SectionCard } from "~/components/infra/section-card";
import { ActionSingle, SectionActions } from "~/components/infra/section-actions";
import { useContext } from "react";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
  itemId: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    isDone: CheckboxAsString,
    tags: z
      .string()
      .transform((s) => (s.trim() !== "" ? s.trim().split(",") : [])),
    url: z
      .string()
      .transform((s) => (s === "" ? undefined : s))
      .optional(),
  }),
  z.object({
    intent: z.literal("create-note"),
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
  const { itemId } = parseParams(params, ParamsSchema);

  try {
    const result = await apiClient.item.smartListItemLoad({
      ref_id: itemId,
      allow_archived: true,
    });

    return json({
      item: result.item,
      tags: result.tags,
      note: result.note,
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id, itemId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.item.smartListItemUpdate({
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

        return redirect(`/app/workspace/smart-lists/${id}/items`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.SMART_LIST_ITEM,
          source_entity_ref_id: itemId,
          content: [],
        });

        return redirect(`/app/workspace/smart-lists/${id}/items/${itemId}`);
      }

      case "archive": {
        await apiClient.item.smartListItemArchive({
          ref_id: itemId,
        });

        return redirect(`/app/workspace/smart-lists/${id}/items`);
      }

      case "remove": {
        await apiClient.item.smartListItemRemove({
          ref_id: itemId,
        });

        return redirect(`/app/workspace/smart-lists/${id}/items`);
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
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.item.archived;

  return (
    <LeafPanel
      fakeKey={`smart-list-${id}/item-${loaderData.item.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.item.archived}
      returnLocation={`/app/workspace/smart-lists/${id}/items`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard title="Properties"
        actions={
          <SectionActions
            id="email-task-actions"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Save",
                value: "update",
                highlight: true,
              }),
            ]}
          />
        }>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                defaultValue={loaderData.item.name}
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
                    defaultChecked={loaderData.item.is_done}
                  />
                }
                label="Is Done"
              />
              <FieldError actionResult={actionData} fieldName="/is_done" />
            </FormControl>

            <FormControl fullWidth>
              <TagsEditor
                allTags={loaderData.tags}
                defaultTags={loaderData.item.tags_ref_id}
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/tags" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="url">Url [Optional]</InputLabel>
              <OutlinedInput
                label="Url"
                name="url"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.item.url}
              />
              <FieldError actionResult={actionData} fieldName="/url" />
            </FormControl>
          </Stack>
      </SectionCard>

      <SectionCard title="Note"
        actions={
          <SectionActions
            id="smart-list-item-note"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Create Note",
                value: "create-note",
                highlight: false,
                disabled: loaderData.note !== null,
              }),
            ]} />
          }
      >
        {loaderData.note && (
          <>
            <EntityNoteEditor
              initialNote={loaderData.note}
              inputsEnabled={inputsEnabled}
            />
          </>
        )}
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/smart-lists",
  ParamsSchema,
  {
    notFound: (params) =>
      `Could not find item ${params.itemId} in smart list ${params.id}!`,
    error: (params) =>
      `There was an error loading item ${params.itemId} in smart list ${params.id}! Please try again!`,
  },
);
