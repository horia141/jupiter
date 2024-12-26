import { ApiError, WorkspaceFeature } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { WorkspaceFeatureFlagsEditor } from "~/components/feature-flags-editor";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
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

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const result = await apiClient.workspaces.workspaceLoad({});

  return json({
    workspace: result.workspace,
  });
}

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.workspaces.workspaceUpdate({
          name: {
            should_change: true,
            value: form.name,
          },
        });

        return redirect(`/workspace/settings`);
      }

      case "change-feature-flags": {
        await apiClient.workspaces.workspaceChangeFeatureFlags({
          feature_flags: form.featureFlags,
        });

        return redirect(`/workspace/settings`);
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
  const transition = useTransition();

  const globalProperties = useContext(GlobalPropertiesContext);
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <TrunkPanel key={"settings"} returnLocation="/workspace">
      <ToolPanel>
        <Stack useFlexGap gap={2}>
          <Card>
            <GlobalError intent="update" actionResult={actionData} />

            <CardHeader title="General" />
            <CardContent>
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

          <Card>
            <GlobalError
              intent="change-feature-flags"
              actionResult={actionData}
            />

            <CardHeader title="Feature Flags" />

            <CardContent>
              <WorkspaceFeatureFlagsEditor
                name="featureFlags"
                inputsEnabled={inputsEnabled}
                featureFlagsControls={topLevelInfo.workspaceFeatureFlagControls}
                defaultFeatureFlags={loaderData.workspace.feature_flags}
                hosting={globalProperties.hosting}
              />
            </CardContent>

            <CardActions>
              <ButtonGroup>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="change-feature-flags"
                >
                  Change Feature Flags
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error updating the workspace! Please try again!`
);
