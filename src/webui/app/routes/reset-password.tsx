import { ApiError } from "@jupiter/webapi-client";
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
import type { LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Form, Link, useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getGuestApiClient } from "~/api-clients.server";
import { CommunityLink } from "~/components/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/logo";
import { Password } from "~/components/password";
import { Title } from "~/components/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isDevelopment } from "~/logic/domain/env";
import { isInGlobalHosting } from "~/logic/domain/hosting";
import { AUTH_TOKEN_NAME } from "~/names";
import { commitSession, getSession } from "~/sessions";

const RecoverAccountFormSchema = {
  emailAddress: z.string(),
  recoveryToken: z.string(),
  newPassword: z.string(),
  newPasswordRepeat: z.string(),
};

// @secureFn
export async function loader({ request }: LoaderArgs) {
  return json({});
}

// @secureFn
export async function action({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const apiClient = await getGuestApiClient(request);
  const form = await parseForm(request, RecoverAccountFormSchema);

  try {
    const resetPasswordResult = await apiClient.auth.resetPassword({
      email_address: form.emailAddress,
      recovery_token: form.recoveryToken,
      new_password: form.newPassword,
      new_password_repeat: form.newPasswordRepeat,
    });

    const loginResult = await apiClient.login.login({
      email_address: form.emailAddress,
      password: form.newPassword,
    });

    session.set(AUTH_TOKEN_NAME, loginResult.auth_token_ext);

    return redirect(
      `/show-recovery-token?recoveryToken=${resetPasswordResult.new_recovery_token}`,
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

export default function ResetPassword() {
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const globalProperties = useContext(GlobalPropertiesContext);

  const inputsEnabled = transition.state === "idle";

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
            <CardHeader title="Reset Password" />
            <CardContent>
              <Stack spacing={2}>
                <FormControl fullWidth>
                  <InputLabel htmlFor="emailAddress">Email Address</InputLabel>
                  <OutlinedInput
                    label="Email Address"
                    name="emailAddress"
                    type="email"
                    autoComplete="email"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/email_address"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel htmlFor="recoveryToken">
                    Recovery Token
                  </InputLabel>
                  <OutlinedInput
                    label="Recovery Token"
                    name="recoveryToken"
                    type="text"
                    autoComplete="off"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/recovery_token"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel htmlFor="newPassword">New Password</InputLabel>
                  <Password
                    label="New Password"
                    name="newPassword"
                    autoComplete="new-password"
                    inputsEnabled={inputsEnabled}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/new_password"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel htmlFor="newPasswordRepeat">
                    Repeat New Password
                  </InputLabel>
                  <Password
                    label="Repeat New Password"
                    name="newPasswordRepeat"
                    inputsEnabled={inputsEnabled}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/new_password_repeat"
                  />
                </FormControl>
              </Stack>
            </CardContent>

            <CardActions>
              <ButtonGroup>
                <Button
                  id="reset-password"
                  type="submit"
                  variant="contained"
                  disabled={!inputsEnabled}
                >
                  Reset Password
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>
        </Form>

        <EntityActionHeader>
          <Button variant="outlined" component={Link} to="/login">
            Login
          </Button>

          <Button variant="outlined" component={Link} to="/init">
            New Workspace
          </Button>
        </EntityActionHeader>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
