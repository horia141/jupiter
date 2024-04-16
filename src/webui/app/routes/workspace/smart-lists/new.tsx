import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError } from "@jupiter/webapi-client";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { IconSelector } from "~/components/icon-selector";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const CreateFormSchema = {
  name: z.string(),
  icon: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await getLoggedInApiClient(
      session
    ).smartLists.smartListCreate({
      name: form.name,
      icon: form.icon,
    });

    return redirect(
      `/workspace/smart-lists/${result.new_smart_list.ref_id}/items`
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function NewSmartList() {
  const transition = useTransition();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel returnLocation="/workspace/smart-lists">
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
                label="Name"
                name="name"
                readOnly={!inputsEnabled}
              />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="icon">Icon</InputLabel>
              <IconSelector readOnly={!inputsEnabled} />
              <FieldError actionResult={actionData} fieldName="/icon" />
            </FormControl>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="smart-list-create"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
            >
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the smart list! Please try again!`
);
