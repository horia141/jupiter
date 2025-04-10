import { ApiError } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  OutlinedInput,
} from "@mui/material";
import { Stack } from "@mui/system";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

const ParamsSchema = z.object({});

const CreateFormSchema = z.object({
  name: z.string(),
  startDate: z.string(),
  endDate: z.string(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.vacations.vacationCreate({
      name: form.name,
      start_date: form.startDate,
      end_date: form.endDate,
    });

    return redirect(`/app/workspace/vacations/${result.new_vacation.ref_id}`);
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

export default function NewVacation() {
  const navigation = useNavigation();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={"vacations/new"}
      returnLocation="/app/workspace/vacations"
      inputsEnabled={inputsEnabled}
    >
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
              <InputLabel id="startDate" shrink margin="dense">
                Start Date
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="startDate"
                name="startDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/start_date" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="endDate" shrink margin="dense">
                End Date
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="endDate"
                name="endDate"
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={actionData} fieldName="/end_date" />
            </FormControl>
          </Stack>
        </CardContent>
        <CardActions>
          <ButtonGroup>
            <Button
              id="vacation-create"
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="create"
            >
              Create
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/vacations",
  ParamsSchema,
  {
    error: () => `There was an error creating the vacation! Please try again!`,
  },
);
