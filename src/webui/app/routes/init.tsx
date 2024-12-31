import {
  ApiError,
  UserFeature,
  WorkspaceFeature,
} from "@jupiter/webapi-client";
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
  Typography,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  Form,
  Link,
  useActionData,
  useLoaderData,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getGuestApiClient } from "~/api-clients.server";
import { CommunityLink } from "~/components/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import {
  UserFeatureFlagsEditor,
  WorkspaceFeatureFlagsEditor,
} from "~/components/feature-flags-editor";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/logo";
import { Title } from "~/components/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isDevelopment } from "~/logic/domain/env";
import { isInGlobalHosting } from "~/logic/domain/hosting";
import { AUTH_TOKEN_NAME } from "~/names";
import { commitSession, getSession } from "~/sessions";

const WorkspaceInitFormSchema = {
  userEmailAddress: z.string(),
  userName: z.string(),
  userTimezone: z.string(),
  userFeatureFlags: z
    .array(z.nativeEnum(UserFeature))
    .or(z.nativeEnum(UserFeature).transform((v) => [v])),
  authPassword: z.string(),
  authPasswordRepeat: z.string(),
  workspaceName: z.string(),
  workspaceRootProjectName: z.string(),
  workspaceFirstScheduleStreamName: z.string(),
  workspaceFeatureFlags: z.array(z.nativeEnum(WorkspaceFeature)),
};

// @secureFn
export async function loader({ request }: LoaderArgs) {
  const apiClient = await getGuestApiClient(request);
  const result = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});
  if (result.user || result.workspace) {
    return redirect("/workspace");
  }

  return json({
    userFeatureFlagControls: result.user_feature_flag_controls,
    defaultUserFeatureFlags: result.default_user_feature_flags,
    defaultWorkspaceName: result.deafult_workspace_name,
    defaultRootProjectName: result.default_root_project_name,
    defaultFirstScheduleStreamName: result.default_first_schedule_stream_name,
    workspaceFeatureFlagControls: result.workspace_feature_flag_controls,
    defaultWorkspaceFeatureFlags: result.default_workspace_feature_flags,
  });
}

// @secureFn
export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const apiClient = await getGuestApiClient(request);
  const form = await parseForm(request, WorkspaceInitFormSchema);

  try {
    const result = await apiClient.application.init({
      user_email_address: form.userEmailAddress,
      user_name: form.userName,
      user_timezone: form.userTimezone,
      user_feature_flags: form.userFeatureFlags,
      auth_password: form.authPassword,
      auth_password_repeat: form.authPasswordRepeat,
      workspace_name: form.workspaceName,
      workspace_root_project_name: form.workspaceRootProjectName,
      workspace_first_schedule_stream_name:
        form.workspaceFirstScheduleStreamName,
      workspace_feature_flags: form.workspaceFeatureFlags,
    });

    session.set(AUTH_TOKEN_NAME, result.auth_token_ext);

    return redirect(
      `/show-recovery-token?recoveryToken=${result.recovery_token}`,
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
  const loaderData = useLoaderData<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const allTimezonesAsOptions = (Intl as any).supportedValuesOf("timeZone");

  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />

        <Title />

        {(isInGlobalHosting(globalProperties.hosting) ||
          isDevelopment(globalProperties.env)) && <CommunityLink />}

        <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />
      </SmartAppBar>

      <LifecyclePanel>
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
                  <FieldError
                    actionResult={actionData}
                    fieldName="/user_name"
                  />
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
                  <InputLabel id="authPasswordRepeat">
                    Password Repeat
                  </InputLabel>
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

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Advanced</Typography>
                  </AccordionSummary>

                  <AccordionDetails>
                    <Stack spacing={2} useFlexGap>
                      <FormControl fullWidth>
                        <InputLabel id="workspaceName">
                          Workspace Name
                        </InputLabel>
                        <OutlinedInput
                          label="Workspace Name"
                          name="workspaceName"
                          readOnly={!inputsEnabled}
                          defaultValue={loaderData.defaultWorkspaceName}
                        />
                        <FieldError
                          actionResult={actionData}
                          fieldName="/workspace_name"
                        />
                      </FormControl>

                      <FormControl fullWidth>
                        <InputLabel id="name">Root Project Name</InputLabel>
                        <OutlinedInput
                          label="Root Project Name"
                          name="workspaceRootProjectName"
                          readOnly={!inputsEnabled}
                          defaultValue={loaderData.defaultRootProjectName}
                        />
                        <FieldError
                          actionResult={actionData}
                          fieldName="/workspace_root_project_name"
                        />
                      </FormControl>

                      <FormControl fullWidth>
                        <InputLabel id="name">
                          First Schedule Stream Name
                        </InputLabel>
                        <OutlinedInput
                          label="First Schdule Stream Name"
                          name="workspaceFirstScheduleStreamName"
                          readOnly={!inputsEnabled}
                          defaultValue={
                            loaderData.defaultFirstScheduleStreamName
                          }
                        />
                        <FieldError
                          actionResult={actionData}
                          fieldName="/workspace_first_schedule_stream_name"
                        />
                      </FormControl>
                    </Stack>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Feature Flags</Typography>
                  </AccordionSummary>

                  <AccordionDetails>
                    <UserFeatureFlagsEditor
                      name="userFeatureFlags"
                      inputsEnabled={inputsEnabled}
                      featureFlagsControls={loaderData.userFeatureFlagControls}
                      defaultFeatureFlags={loaderData.defaultUserFeatureFlags}
                      hosting={globalProperties.hosting}
                    />
                    <WorkspaceFeatureFlagsEditor
                      name="workspaceFeatureFlags"
                      inputsEnabled={inputsEnabled}
                      featureFlagsControls={
                        loaderData.workspaceFeatureFlagControls
                      }
                      defaultFeatureFlags={
                        loaderData.defaultWorkspaceFeatureFlags
                      }
                      hosting={globalProperties.hosting}
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
      </LifecyclePanel>
    </StandaloneContainer>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the workspace! Please try again!`
);
