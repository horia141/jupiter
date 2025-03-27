import { ApiError, UserFeature } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { UserFeatureFlagsEditor } from "~/components/feature-flags-editor";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { TimezoneSelect } from "~/components/timezone-select";
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
    timezone: z.string(),
  }),
  z.object({
    intent: z.literal("change-feature-flags"),
    featureFlags: z.array(z.nativeEnum(UserFeature)),
  }),
  z.object({
    intent: z.literal("close-account"),
  }),
]);

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const result = await apiClient.users.userLoad({});

  return json({
    user: result.user,
  });
}

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.users.userUpdate({
          name: {
            should_change: true,
            value: form.name,
          },
          timezone: {
            should_change: true,
            value: form.timezone,
          },
        });

        return redirect(`/app/workspace/account`);
      }

      case "change-feature-flags": {
        await apiClient.users.userChangeFeatureFlags({
          feature_flags: form.featureFlags,
        });

        return redirect(`/app/workspace/account`);
      }

      case "close-account": {
        await apiClient.application.closeAccount({});

        return redirect(`/app/init`);
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

export default function Account() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();

  const globalProperties = useContext(GlobalPropertiesContext);
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  const [showCloseAccountDialog, setShowCloseAccountDialog] = useState(false);

  return (
    <TrunkPanel key={"account"} returnLocation="/app/workspace">
      <ToolPanel>
        <Stack useFlexGap gap={2}>
          <Card>
            <GlobalError actionResult={actionData} />

            <CardHeader title="Account" />
            <CardContent>
              <Stack spacing={2} useFlexGap>
                <FormControl fullWidth>
                  <InputLabel id="emailAddress">Your Email Address</InputLabel>
                  <OutlinedInput
                    type="email"
                    autoComplete="email"
                    label="Your Email Address"
                    name="emailAddress"
                    disabled={true}
                    defaultValue={loaderData.user.email_address}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <TextField
                    name="name"
                    label="Your Name"
                    defaultValue={loaderData.user.name}
                    disabled={!inputsEnabled}
                  />
                  <FieldError actionResult={actionData} fieldName="/name" />
                </FormControl>
                <FormControl fullWidth>
                  <TimezoneSelect
                    id="timezone"
                    name="timezone"
                    inputsEnabled={inputsEnabled}
                    initialValue={loaderData.user.timezone}
                  />

                  <FieldError actionResult={actionData} fieldName="/timezone" />
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
              <UserFeatureFlagsEditor
                name="featureFlags"
                inputsEnabled={inputsEnabled}
                featureFlagsControls={topLevelInfo.userFeatureFlagControls}
                defaultFeatureFlags={loaderData.user.feature_flags}
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

          <Card>
            <GlobalError intent="close-account" actionResult={actionData} />

            <CardHeader title="Dangerous" />

            <Dialog
              onClose={() => setShowCloseAccountDialog(false)}
              open={showCloseAccountDialog}
              disablePortal
            >
              <DialogTitle>Are You Sure?</DialogTitle>
              <DialogContent>
                <Typography variant="body1">
                  Are you sure you want to close your account? This action is
                  irreversible.
                </Typography>
              </DialogContent>
              <DialogActions>
                <Button
                  id="close-account"
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="close-account"
                  color="error"
                >
                  Close Account
                </Button>
              </DialogActions>
            </Dialog>

            <CardActions>
              <ButtonGroup>
                <Button
                  id="close-account-initialize"
                  variant="contained"
                  disabled={!inputsEnabled}
                  onClick={() => setShowCloseAccountDialog(true)}
                  color="error"
                >
                  Close Account
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary(
  "/app/workspace",
  () => `There was an error updating the account! Please try again!`,
);
