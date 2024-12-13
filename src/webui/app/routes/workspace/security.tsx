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
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const SecurityFormSchema = {
  intent: z.string(),
  currentPassword: z.string(),
  newPassword: z.string(),
  newPasswordRepeat: z.string(),
};

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  getLoggedInApiClient(session);
  return json({});
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, SecurityFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "change-password": {
        await getLoggedInApiClient(session).auth.changePassword({
          current_password: form.currentPassword,
          new_password: form.newPassword,
          new_password_repeat: form.newPasswordRepeat,
        });

        return redirect(`/workspace/security`);
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
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <TrunkPanel key={"security"} returnLocation="/workspace">
      <ToolPanel>
        <Stack useFlexGap gap={2}>
          <Card>
            <GlobalError actionResult={actionData} />
            <CardHeader title="Security" />
            <CardContent>
              <Stack spacing={2} useFlexGap>
                <FormControl fullWidth>
                  <InputLabel id="currentPassword">Current Password</InputLabel>
                  <OutlinedInput
                    label="Current Password"
                    type="password"
                    autoComplete="current-password"
                    name="currentPassword"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/current_password"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="newPassword">New Password</InputLabel>
                  <OutlinedInput
                    label="New Password"
                    type="password"
                    autoComplete="new-password"
                    name="newPassword"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
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
                  <OutlinedInput
                    label="New Password Repeat"
                    type="password"
                    autoComplete="off"
                    name="newPasswordRepeat"
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
                  id="change-password"
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="change-password"
                >
                  Change Password
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error changing security settings! Please try again!`
);
