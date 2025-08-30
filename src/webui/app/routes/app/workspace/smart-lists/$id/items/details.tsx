import { ApiError, NoteDomain } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoteEditor } from "~/components/infra/entity-note-editor";
import { IconSelector } from "~/components/infra/icon-selector";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { SectionCard } from "~/components/infra/section-card";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    icon: z.string().optional(),
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
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await apiClient.smartLists.smartListLoad({
      ref_id: id,
      allow_archived: true,
      allow_archived_items: false,
      allow_archived_tags: false,
    });

    return json({
      smartList: response.smart_list,
      note: response.note,
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.smartLists.smartListUpdate({
          ref_id: id,
          name: {
            should_change: true,
            value: form.name,
          },
          icon: {
            should_change: true,
            value: form.icon,
          },
        });

        return redirect(`/app/workspace/smart-lists/${id}/items`);
      }

      case "create-note": {
        await apiClient.notes.noteCreate({
          domain: NoteDomain.SMART_LIST,
          source_entity_ref_id: id,
          content: [],
        });

        return redirect(`/app/workspace/smart-lists/${id}/items/details`);
      }

      case "archive": {
        await apiClient.smartLists.smartListArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/smart-lists/${id}/items`);
      }

      case "remove": {
        await apiClient.smartLists.smartListRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/smart-lists`);
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function SmartListDetails() {
  const { id } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.smartList.archived;

  return (
    <LeafPanel
      key={`smart-list-${id}/details`}
      fakeKey={`smart-list-${id}/details`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.smartList.archived}
      returnLocation={`/app/workspace/smart-lists/${id}/items`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="Properties"
        actions={
          <SectionActions
            id="smart-list-properties"
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
        }
      >
        <FormControl fullWidth>
          <InputLabel id="name">Name</InputLabel>
          <OutlinedInput
            label="Name"
            name="name"
            readOnly={!inputsEnabled}
            defaultValue={loaderData.smartList.name}
          />
          <FieldError actionResult={actionData} fieldName="/name" />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="icon">Icon</InputLabel>
          <IconSelector
            readOnly={!inputsEnabled}
            defaultIcon={loaderData.smartList.icon}
          />
          <FieldError actionResult={actionData} fieldName="/icon" />
        </FormControl>
      </SectionCard>

      <SectionCard
        title="Note"
        actions={
          <SectionActions
            id="smart-list-note"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Create Note",
                value: "create-note",
                highlight: false,
                disabled: loaderData.note !== null,
              }),
            ]}
          />
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
  (params) => `/app/workspace/smart-lists/${params.id}/items`,
  ParamsSchema,
  {
    notFound: (params) =>
      `Could not find smart list item details for #${params.id}!`,
    error: (params) =>
      `There was an error loading smart list item details for #${params.id}! Please try again!`,
  },
);
