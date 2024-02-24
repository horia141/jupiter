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
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getGuestApiClient } from "~/api-clients";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
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
  const form = await parseForm(request, RecoverAccountFormSchema);

  try {
    const resetPasswordResult = await getGuestApiClient(
      session
    ).auth.resetPassword({
      email_address: form.emailAddress,
      recovery_token: form.recoveryToken,
      new_password: form.newPassword,
      new_password_repeat: form.newPasswordRepeat,
    });

    const loginResult = await getGuestApiClient(session).login.login({
      email_address: form.emailAddress,
      password: form.newPassword,
    });

    session.set("authTokenExt", loginResult.auth_token_ext);

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

  const inputsEnabled = transition.state === "idle";

  return (
    <StandaloneContainer>
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
                <InputLabel htmlFor="recoveryToken">Recovery Token</InputLabel>
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
                <OutlinedInput
                  label="New Password"
                  name="newPassword"
                  type="password"
                  autoComplete="new-password"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
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
                <OutlinedInput
                  label="Repeat New Password"
                  name="newPasswordRepeat"
                  type="password"
                  autoComplete="new-password"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
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
    </StandaloneContainer>
  );
}
