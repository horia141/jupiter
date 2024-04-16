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
import { Form, Link, useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "@jupiter/webapi-client";
import { z } from "zod";
import { parseForm } from "zodix";
import { getGuestApiClient } from "~/api-clients";
import { EntityActionHeader } from "~/components/infra/entity-actions-header";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { DisplayType } from "~/rendering/use-nested-entities";
import { commitSession, getSession } from "~/sessions";

const LoginFormSchema = {
  emailAddress: z.string(),
  password: z.string(),
};

export const handle = {
  displayType: DisplayType.ROOT,
};

// @secureFn
export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));

  if (session.has("authTokenExt")) {
    const apiClient = getGuestApiClient(session);
    const result = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});
    if (result.user || result.workspace) {
      return redirect("/workspace");
    }
  }

  return json({});
}

// @secureFn
export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, LoginFormSchema);

  try {
    const result = await getGuestApiClient(session).login.login({
      email_address: form.emailAddress,
      password: form.password,
    });

    session.set("authTokenExt", result.auth_token_ext);

    // Login succeeded, send them to the home page.
    return redirect("/workspace", {
      headers: {
        "Set-Cookie": await commitSession(session),
      },
    });
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

// @secureFn
export default function Login() {
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <StandaloneContainer>
      <Form method="post">
        <Card>
          <GlobalError actionResult={actionData} />
          <CardHeader title="Login" />
          <CardContent>
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="emailAddress">Email Address</InputLabel>
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
                <InputLabel id="password">Password</InputLabel>
                <OutlinedInput
                  label="Password"
                  type="password"
                  autoComplete="current-password"
                  name="password"
                  readOnly={!inputsEnabled}
                  defaultValue={""}
                />
                <FieldError actionResult={actionData} fieldName="/password" />
              </FormControl>
            </Stack>
          </CardContent>

          <CardActions>
            <ButtonGroup>
              <Button
                id="login"
                variant="contained"
                disabled={!inputsEnabled}
                type="submit"
              >
                Login
              </Button>
            </ButtonGroup>
          </CardActions>
        </Card>
      </Form>

      <EntityActionHeader>
        <Button
          variant="outlined"
          disabled={!inputsEnabled}
          to={`/init`}
          component={Link}
        >
          New Workspace
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
    </StandaloneContainer>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error logging in! Please try again!`
);
