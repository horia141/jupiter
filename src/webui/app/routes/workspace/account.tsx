import {
  Autocomplete,
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
  TextField,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  ShouldRevalidateFunction,
  useActionData,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError, UserFeature } from "jupiter-gen";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { UserFeatureFlagsEditor } from "~/components/feature-flags-editor";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel2 } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const AccountFormSchema = {
  intent: z.string(),
  name: z.string(),
  timezone: z.string(),
  featureFlags: z
    .nativeEnum(UserFeature)
    .transform((s) => [s])
    .optional()
    .transform((_) => []),
};

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const result = await getLoggedInApiClient(session).user.loadUser({});

  return json({
    user: result.user,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, AccountFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "update": {
        await getLoggedInApiClient(session).user.updateUser({
          name: {
            should_change: true,
            value: { the_name: form.name },
          },
          timezone: {
            should_change: true,
            value: { the_timezone: form.timezone },
          },
        });

        return redirect(`/workspace/account`);
      }

      case "change-feature-flags": {
        const featureFlags: Record<string, boolean> = {};
        for (const feature of Object.values(UserFeature)) {
          if (form.featureFlags.find((v) => v == feature)) {
            featureFlags[feature] = true;
          } else {
            featureFlags[feature] = false;
          }
        }

        await getLoggedInApiClient(session).user.changeUserFeatureFlags({
          feature_flags: featureFlags,
        });

        return redirect(`/workspace/account`);
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
  const transition = useTransition();

  const globalProperties = useContext(GlobalPropertiesContext);
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const allTimezonesAsOptions = (Intl as any).supportedValuesOf("timeZone");

  return (
    <TrunkPanel>
      <ToolPanel2 returnLocation="/workspace">
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
                    defaultValue={loaderData.user.email_address.the_address}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <TextField
                    name="name"
                    label="Your Name"
                    defaultValue={loaderData.user.name.the_name}
                    disabled={!inputsEnabled}
                  />
                  <FieldError actionResult={actionData} fieldName="/name" />
                </FormControl>
                <FormControl fullWidth>
                  <Autocomplete
                    id="timezone"
                    options={allTimezonesAsOptions}
                    readOnly={!inputsEnabled}
                    defaultValue={loaderData.user.timezone.the_timezone}
                    disableClearable={true}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        name="timezone"
                        label="Your Timezone"
                      />
                    )}
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
        </Stack>
      </ToolPanel2>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error updating the account! Please try again!`
);
