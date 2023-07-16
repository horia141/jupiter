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
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolCard } from "~/components/infra/tool-card";
import { ToolPanel } from "~/components/infra/tool-panel";
import { TrunkCard } from "~/components/infra/trunk-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { getIntent } from "~/logic/intent";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const SecurityFormSchema = {
  intent: z.string(),
  currentPassword: z.string(),
  newPassword: z.string(),
  newPasswordRepeat: z.string(),
};

export const handle = {
  displayType: DisplayType.TRUNK,
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
          current_password: {
            password_raw: form.currentPassword,
          },
          new_password: {
            password_raw: form.newPassword,
          },
          new_password_repeat: {
            password_raw: form.newPasswordRepeat,
          },
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

export default function Security() {
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <TrunkCard>
      <ToolPanel show={true}>
        <ToolCard returnLocation="/workspace">
          <GlobalError actionResult={actionData} />
          <Card>
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
        </ToolCard>
      </ToolPanel>
    </TrunkCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error changing security settings! Please try again!`
);
