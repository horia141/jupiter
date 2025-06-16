import { ApiError } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ActionSingle, SectionActions } from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({
  id: z.string(),
  tagId: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
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
  const { tagId } = parseParams(params, ParamsSchema);

  try {
    const result = await apiClient.tag.smartListTagLoad({
      ref_id: tagId,
      allow_archived: true,
    });

    return json({
      smartListTag: result.smart_list_tag,
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
  const { id, tagId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.tag.smartListTagUpdate({
          ref_id: tagId,
          tag_name: {
            should_change: true,
            value: form.name,
          },
        });

        return redirect(`/app/workspace/smart-lists/${id}/tags`);
      }

      case "archive": {
        await apiClient.tag.smartListTagArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/smart-lists/${id}/tags`);
      }

      case "remove": {
        await apiClient.tag.smartListTagRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/smart-lists/${id}/tags`);
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

export default function SmartListTag() {
  const { id, tagId } = useParams();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.smartListTag.archived;

  return (
    <LeafPanel
      fakeKey={`smart-list-${id}/tag-${tagId}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.smartListTag.archived}
      returnLocation={`/app/workspace/smart-lists/${id}/tags`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard title="Properties"
        actions={
          <SectionActions
            id="smart-list-tag-properties"
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
                defaultValue={loaderData.smartListTag.tag_name}
                name="name"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/tag_name" />
            </FormControl>
          </Stack>
          </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  (params) => `/app/workspace/smart-lists/${params.id}/tags`,
  ParamsSchema,
  {
    notFound: (params) => `Could not find smart list tag #${params.tagId}!`,
    error: (params) =>
      `There was an error loading smart list tag #${params.tagId}! Please try again!`,
  },
);
