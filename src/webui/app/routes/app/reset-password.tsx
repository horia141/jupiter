import { ApiError } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";

import { getGuestApiClient } from "~/api-clients.server";
import { CommunityLink } from "~/components/infra/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/infra/docs-help";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/infra/logo";
import { Password } from "~/components/domain/application/auth/password";
import { Title } from "~/components/infra/title";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { AUTH_TOKEN_NAME } from "~/names";
import { commitSession, getSession } from "~/sessions";
import {
  ActionSingle,
  ActionsExpansion,
  NavSingle,
  NavMultipleCompact,
  SectionActions,
} from "~/components/infra/section-actions";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import { EMPTY_CONTEXT } from "~/top-level-context";

const RecoverAccountFormSchema = z.object({
  emailAddress: z.string(),
  recoveryToken: z.string(),
  newPassword: z.string(),
  newPasswordRepeat: z.string(),
});

// @secureFn
export async function action({ request }: LoaderFunctionArgs) {
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
      `/app/show-recovery-token?recoveryToken=${resetPasswordResult.new_recovery_token}`,
      {
        headers: {
          "Set-Cookie": await commitSession(session),
        },
      },
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
  const navigation = useNavigation();
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
          title="Reset Password"
          actionsPosition={ActionsPosition.BELOW}
          actions={
            <SectionActions
              id="reset-password"
              topLevelInfo={EMPTY_CONTEXT}
              inputsEnabled={inputsEnabled}
              expansion={ActionsExpansion.ALWAYS_SHOW}
              actions={[
                ActionSingle({
                  text: "Reset Password",
                  value: "reset",
                  highlight: true,
                }),
                NavMultipleCompact({
                  navs: [
                    NavSingle({
                      text: "Login",
                      link: "/app/login",
                    }),
                    NavSingle({
                      text: "New Workspace",
                      link: "/app/init",
                    }),
                  ],
                }),
              ]}
            />
          }
        >
          <Stack spacing={2} useFlexGap>
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
              <Password
                label="New Password"
                name="newPassword"
                autoComplete="new-password"
                inputsEnabled={inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/new_password" />
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
        </SectionCard>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
