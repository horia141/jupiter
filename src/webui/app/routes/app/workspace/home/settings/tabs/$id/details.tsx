import { ApiError } from "@jupiter/webapi-client";
import { FormControl, InputLabel, TextField } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  SectionActions,
  ActionSingle,
} from "~/components/infra/section-actions";
import { SectionCard } from "~/components/infra/section-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { IconSelector } from "~/components/infra/icon-selector";

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    icon: z.string(),
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

  const result = await apiClient.tab.homeTabLoad({
    ref_id: id,
    allow_archived: true,
  });

  return json(result);
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update":
        await apiClient.tab.homeTabUpdate({
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

        return redirect(`/app/workspace/home/settings/tabs/${id}`);

      case "archive":
        await apiClient.tab.homeTabArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/home/settings/tabs/${id}`);

      case "remove":
        await apiClient.tab.homeTabRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/home/settings`);

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

export default function HomeTabDetails() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={`home-tab-details-${loaderData.tab.ref_id}`}
      fakeKey={`home-tab-details-${loaderData.tab.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.tab.archived}
      returnLocation={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}`}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        id="home-tab-details"
        title="Tab Details"
        actions={
          <SectionActions
            id="home-tab-details"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "home-tab-details-update",
                text: "Update",
                value: "update",
                disabled: !inputsEnabled,
                highlight: true,
              }),
            ]}
          />
        }
      >
        <FormControl fullWidth>
          <TextField
            name="name"
            label="Name"
            defaultValue={loaderData.tab.name}
            disabled={!inputsEnabled}
          />
          <FieldError actionResult={actionData} fieldName="/name" />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="icon">Icon</InputLabel>
          <IconSelector
            readOnly={!inputsEnabled}
            defaultIcon={loaderData.tab.icon}
          />
          <FieldError actionResult={actionData} fieldName="/icon" />
        </FormControl>
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/home/settings/tabs",
  ParamsSchema,
  {
    notFound: (params) => `Could not find tab #${params.id}!`,
    error: (params) =>
      `There was an error loading tab #${params.id}! Please try again!`,
  },
);
