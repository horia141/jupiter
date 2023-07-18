import {
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
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const AccountFormSchema = {
  intent: z.string(),
  name: z.string(),
  timezone: z.string(),
};

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const result = await getLoggedInApiClient(session).user.loadUser({});

  return json({
    user: result.user,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, AccountFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "update": {
        await getLoggedInApiClient(session).user.updateUser({
          name: {
            should_change: true,
            value: { the_name: form.name },
          },
          timezone: {
            should_change: true,
            value: { the_timezone: form.timezone },
          },
        });

        return redirect(`/workspace/account`);
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

export default function Account() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const allTimezonesAsOptions = (Intl as any).supportedValuesOf("timeZone");

  return (
    <TrunkCard>
      <ToolPanel show={true}>
        <ToolCard returnLocation="/workspace">
          <Card>
            <GlobalError actionResult={actionData} />

            <CardHeader title="Account" />
            <CardContent>
              <Stack spacing={2} useFlexGap>
                <FormControl fullWidth>
                  <InputLabel id="emailAddress">Your Email Address</InputLabel>
                  <OutlinedInput
                    type="email"
                    autoComplete="email"
                    label="Your Email Address"
                    name="emailAddress"
                    disabled={true}
                    defaultValue={loaderData.user.email_address.the_address}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <TextField
                    name="name"
                    label="Your Name"
                    defaultValue={loaderData.user.name.the_name}
                    disabled={!inputsEnabled}
                  />
                  <FieldError actionResult={actionData} fieldName="/name" />
                </FormControl>
                <FormControl fullWidth>
                  <Autocomplete
                    id="timezone"
                    options={allTimezonesAsOptions}
                    readOnly={!inputsEnabled}
                    defaultValue={loaderData.user.timezone.the_timezone}
                    disableClearable={true}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        name="timezone"
                        label="Your Timezone"
                      />
                    )}
                  />

                  <FieldError actionResult={actionData} fieldName="/timezone" />
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
                  value="update"
                >
                  Save
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
  () => `There was an error updating the account! Please try again!`
);
