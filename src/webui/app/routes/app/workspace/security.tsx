import { ApiError } from "@jupiter/webapi-client";
import { FormControl, InputLabel, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeTrunkErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { Password } from "~/components/domain/application/auth/password";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { SectionCard } from "~/components/infra/section-card";
import { SectionActions , ActionSingle } from "~/components/infra/section-actions";
import { TopLevelInfoContext } from "~/top-level-context";

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("change-password"),
    currentPassword: z.string(),
    newPassword: z.string(),
    newPasswordRepeat: z.string(),
  }),
]);

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderFunctionArgs) {
  await getLoggedInApiClient(request);
  return json({});
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "change-password": {
        await apiClient.auth.changePassword({
          current_password: form.currentPassword,
          new_password: form.newPassword,
          new_password_repeat: form.newPasswordRepeat,
        });

        return redirect(`/app/workspace/security`);
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

export default function Security() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "idle";
  const topLevelInfo = useContext(TopLevelInfoContext);

  return (
    <TrunkPanel key={"security"} returnLocation="/app/workspace">
      <ToolPanel>
        <GlobalError actionResult={actionData} />
        <Stack useFlexGap gap={2}>
          <SectionCard
            id="security"
            title="Security"
            actions={
              <SectionActions
                id="security-actions"
                topLevelInfo={topLevelInfo}
                inputsEnabled={inputsEnabled}
                actions={[
                  ActionSingle({
                    text: "Change Password",
                    value: "change-password",
                    highlight: true,
                  }),
                ]}
              />
            }
          >
            <Stack spacing={2} useFlexGap>
              <FormControl fullWidth>
                <InputLabel id="currentPassword">Current Password</InputLabel>
                <Password
                  label="Current Password"
                  name="currentPassword"
                  autoComplete="current-password"
                  inputsEnabled={inputsEnabled}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/current_password"
                />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="newPassword">New Password</InputLabel>
                <Password
                  label="newPassword"
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
                <InputLabel id="newPasswordRepeat">
                  New Password Repeat
                </InputLabel>
                <Password
                  label="New Password Repeat"
                  name="newPasswordRepeat"
                  autoComplete="new-password"
                  inputsEnabled={inputsEnabled}
                />
                <FieldError
                  actionResult={actionData}
                  fieldName="/new_password_repeat"
                />
              </FormControl>
            </Stack>
          </SectionCard>
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeTrunkErrorBoundary("/app/workspace", {
  error: () =>
    `There was an error changing security settings! Please try again!`,
});
