import { ApiError, AppShell } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getGuestApiClient } from "~/api-clients.server";
import { CommunityLink } from "~/components/infra/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/infra/docs-help";
import { makeRootErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/infra/logo";
import { Password } from "~/components/domain/application/auth/password";
import { Title } from "~/components/infra/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { AUTH_TOKEN_NAME } from "~/names";
import { DisplayType } from "~/rendering/use-nested-entities";
import { commitSession, getSession } from "~/sessions";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import {
  ActionSingle,
  NavSingle,
  NavMultipleCompact,
 ActionsExpansion , SectionActions } from "~/components/infra/section-actions";
import { EMPTY_CONTEXT } from "~/top-level-context";

const LoginFormSchema = z.object({
  emailAddress: z.string(),
  password: z.string(),
});

export const handle = {
  displayType: DisplayType.ROOT,
};

// @secureFn
export async function loader({ request }: LoaderFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const apiClient = await getGuestApiClient(request);

  if (session.has(AUTH_TOKEN_NAME)) {
    const result = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});
    if (result.user || result.workspace) {
      return redirect("/app/workspace");
    }
  }

  return json({});
}

// @secureFn
export async function action({ request }: ActionFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const apiClient = await getGuestApiClient(request);
  const form = await parseForm(request, LoginFormSchema);

  try {
    const result = await apiClient.login.login({
      email_address: form.emailAddress,
      password: form.password,
    });

    session.set(AUTH_TOKEN_NAME, result.auth_token_ext);

    // Login succeeded, send them to the home page.
    return redirect("/app/workspace", {
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
  const navigation = useNavigation();

  const globalProperties = useContext(GlobalPropertiesContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />

        <Title />

        <CommunityLink />

        <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />
      </SmartAppBar>

      <LifecyclePanel>
        <GlobalError actionResult={actionData} />
        <SectionCard
          title="Login"
          actionsPosition={ActionsPosition.BELOW}
          actions={
            <SectionActions
              id="login"
              topLevelInfo={EMPTY_CONTEXT}
              inputsEnabled={inputsEnabled}
              expansion={ActionsExpansion.ALWAYS_SHOW}
              actions={[
                ActionSingle({
                  text: "Login",
                  value: "login",
                  highlight: true,
                }),
                NavMultipleCompact({
                  navs: [
                    NavSingle({
                      text: "New Workspace",
                      link: "/app/init",
                    }),
                    NavSingle({
                      text: "Reset Password",
                      link: "/app/reset-password",
                    }),
                    NavSingle({
                      text: "Pick Server",
                      link: "/app/pick-server/desktop",
                      disabled:
                        globalProperties.frontDoorInfo.appShell !==
                        AppShell.DESKTOP_ELECTRON,
                    }),
                  ],
                }),
              ]}
            />
          }
        >
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
              <Password
                label="Password"
                name="password"
                autoComplete="current-password"
                inputsEnabled={inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/password" />
            </FormControl>
          </Stack>
        </SectionCard>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}

export const ErrorBoundary = makeRootErrorBoundary({
  error: () => `There was an error logging in! Please try again!`,
});
