import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
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
import { Form, Link, useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError, Feature } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getGuestApiClient } from "~/api-clients";
import { FeatureFlagsEditor } from "~/components/feature-flags-editor";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { StandaloneCard } from "~/components/infra/standalone-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { commitSession, getSession } from "~/sessions";

const WorkspaceInitFormSchema = {
  userEmailAddress: z.string(),
  userName: z.string(),
  userTimezone: z.string(),
  authPassword: z.string(),
  authPasswordRepeat: z.string(),
  workspaceName: z.string(),
  workspaceFirstProjectName: z.string(),
  workspaceFeatureFlags: z.array(z.nativeEnum(Feature)),
};

// @secureFn
export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const apiClient = getGuestApiClient(session);
  const result = await apiClient.loadUserAndWorkspace.loadUserAndWorkspace({});
  if (result.user || result.workspace) {
    return redirect("/workspace");
  }

  return json({
    hosting: result.hosting,
    featureFlagsControl: result.feature_flag_controls,
    defaultFeatureFlags: result.default_feature_flags,
  });
}

// @secureFn
export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, WorkspaceInitFormSchema);

  const workspaceFeatureFlags: Record<string, boolean> = {};
  for (const feature of Object.values(Feature)) {
    if (form.workspaceFeatureFlags.find((v) => v == feature)) {
      workspaceFeatureFlags[feature] = true;
    } else {
      workspaceFeatureFlags[feature] = false;
    }
  }

  try {
    const result = await getGuestApiClient(session).init.init({
      user_email_address: { the_address: form.userEmailAddress },
      user_name: { the_name: form.userName },
      user_timezone: { the_timezone: form.userTimezone },
      auth_password: { password_raw: form.authPassword },
      auth_password_repeat: { password_raw: form.authPasswordRepeat },
      workspace_name: { the_name: form.workspaceName },
      workspace_first_project_name: {
        the_name: form.workspaceFirstProjectName,
      },
      workspace_feature_flags: workspaceFeatureFlags,
    });

    session.set("authTokenExt", result.auth_token_ext);

    return redirect(
      `/show-recovery-token?recoveryToken=${result.recovery_token.token}`,
      {
        headers: {
          "Set-Cookie": await commitSession(session),
        },
      }
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

export default function WorkspaceInit() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const allTimezonesAsOptions = (Intl as any).supportedValuesOf("timeZone");

  return (
    <StandaloneCard>
      <Form method="post">
        <Card>
          <GlobalError actionResult={actionData} />
          <CardHeader title="New Account & Workspace" />
          <CardContent>
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="userEmailAddress">
                  Your Email Address
                </InputLabel>
                <OutlinedInput
                  type="email"
                  autoComplete="email"
                  label="Your Email Address"
                  name="userEmailAddress"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/user_email_address"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="userName">Your Name</InputLabel>
                <OutlinedInput
                  label="Your Name"
                  name="userName"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError actionResult={actionData} fieldName="/user_name" />
              </FormControl>

              <FormControl fullWidth>
                <Autocomplete
                  id="userTimezone"
                  options={allTimezonesAsOptions}
                  readOnly={!inputsEnabled}
                  defaultValue={"Europe/London"}
                  disableClearable={true}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      name="userTimezone"
                      autoComplete="off"
                      label="Your Timezone"
                    />
                  )}
                />

                <FieldError
                  actionResult={actionData}
                  fieldName="/user_timezone"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="authPassword">Password</InputLabel>
                <OutlinedInput
                  label="Password"
                  type="password"
                  autoComplete="new-password"
                  name="authPassword"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/auth_password"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="authPasswordRepeat">Password Repeat</InputLabel>
                <OutlinedInput
                  label="Password Repeat"
                  type="password"
                  name="authPasswordRepeat"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/auth_password_repeat"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="workspaceName">Workspace Name</InputLabel>
                <OutlinedInput
                  label="Workspace Name"
                  name="workspaceName"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/workspace_name"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="name">First Project Name</InputLabel>
                <OutlinedInput
                  label="First Project Name"
                  name="workspaceFirstProjectName"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/workspacefirst_project_name"
                />
              </FormControl>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  Feature Flags
                </AccordionSummary>

                <AccordionDetails>
                  <FeatureFlagsEditor
                    name="workspaceFeatureFlags"
                    inputsEnabled={true}
                    featureFlagsControls={loaderData.featureFlagsControl}
                    defaultFeatureFlags={loaderData.defaultFeatureFlags}
                    hosting={loaderData.hosting}
                  />
                </AccordionDetails>
              </Accordion>
            </Stack>
          </CardContent>

          <CardActions>
            <ButtonGroup>
              <Button
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
              >
                Create
              </Button>
            </ButtonGroup>
          </CardActions>
        </Card>
      </Form>

      <EntityActionHeader>
        <Button
          variant="outlined"
          disabled={!inputsEnabled}
          to={`/login`}
          component={Link}
        >
          Login
        </Button>
        <Button
          variant="outlined"
          disabled={!inputsEnabled}
          to={`/reset-password`}
          component={Link}
        >
          Reset Password
        </Button>
      </EntityActionHeader>
    </StandaloneCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the workspace! Please try again!`
);
