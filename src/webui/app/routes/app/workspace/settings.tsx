import { ApiError, WorkspaceFeature } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirectDocument } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { WorkspaceFeatureFlagsEditor } from "~/components/domain/application/workspace/feature-flags-editor";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { SectionCard } from "~/components/infra/section-card";
import { SectionActions , ActionSingle } from "~/components/infra/section-actions";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
  }),
  z.object({
    intent: z.literal("change-feature-flags"),
    featureFlags: z.array(z.nativeEnum(WorkspaceFeature)),
  }),
]);

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const result = await apiClient.workspaces.workspaceLoad({});

  return json({
    workspace: result.workspace,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  // We do a hard redirect for all actions here, because changing these
  // vary basic properties of the properties, most assuredly will
  // modify topLevelInfo which will need to invalidate all the
  // routes. Since there's some caching over there, we take this
  // simple approach.

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.workspaces.workspaceUpdate({
          name: {
            should_change: true,
            value: form.name,
          },
        });

        return redirectDocument(`/app/workspace/settings`);
      }

      case "change-feature-flags": {
        await apiClient.workspaces.workspaceChangeFeatureFlags({
          feature_flags: form.featureFlags,
        });

        return redirectDocument(`/app/workspace/settings`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body, form.intent));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Settings() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();

  const globalProperties = useContext(GlobalPropertiesContext);
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <TrunkPanel key={"settings"} returnLocation="/app/workspace">
      <ToolPanel>
        <Stack useFlexGap gap={2}>
          <SectionCard
            id="general"
            title="General"
            actions={
              <SectionActions
                id="general-actions"
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
            <GlobalError intent="update" actionResult={actionData} />
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="name">Name</InputLabel>
                <OutlinedInput
                  label="Name"
                  name="name"
                  readOnly={!inputsEnabled}
                  defaultValue={loaderData.workspace.name}
                />
                <FieldError actionResult={actionData} fieldName="/name" />
              </FormControl>
            </Stack>
          </SectionCard>

          <SectionCard
            id="feature-flags"
            title="Feature Flags"
            actions={
              <SectionActions
                id="feature-flags-actions"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  ActionSingle({
                    text: "Change Feature Flags",
                    value: "change-feature-flags",
                    highlight: true,
                  }),
                ]}
              />
            }
          >
            <GlobalError
              intent="change-feature-flags"
              actionResult={actionData}
            />
            <Stack spacing={2} useFlexGap>
              <WorkspaceFeatureFlagsEditor
                name="featureFlags"
                inputsEnabled={inputsEnabled}
                featureFlagsControls={topLevelInfo.workspaceFeatureFlagControls}
                defaultFeatureFlags={loaderData.workspace.feature_flags}
                hosting={globalProperties.hosting}
              />
            </Stack>
          </SectionCard>
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () => `There was an error updating the workspace! Please try again!`,
});
