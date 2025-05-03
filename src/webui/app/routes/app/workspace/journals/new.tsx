import { ApiError, RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
} from "@mui/material";
import { Stack } from "@mui/system";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { PeriodSelect } from "~/components/domain/core/period-select";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({});

const CreateFormSchema = z.object({
  rightNow: z.string(),
  period: z.nativeEnum(RecurringTaskPeriod),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.journals.journalCreate({
      right_now: form.rightNow,
      period: form.period,
    });

    return redirect(`/app/workspace/journals/${result.new_journal.ref_id}`);
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body));
    }

    if (error instanceof ApiError && error.status === StatusCodes.CONFLICT) {
      return json(aGlobalError(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function NewJournal() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={"journasl/new"}
      returnLocation="/app/workspace/journals"
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <Card>
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="rightNow" shrink margin="dense">
                The Date
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="rightNow"
                name="rightNow"
                readOnly={!inputsEnabled}
                defaultValue={DateTime.local({
                  zone: topLevelInfo.user.timezone,
                }).toISODate()}
              />

              <FieldError actionResult={actionData} fieldName="/right_now" />
            </FormControl>

            <FormControl fullWidth>
              <FormLabel id="period">Period</FormLabel>
              <PeriodSelect
                labelId="period"
                label="Period"
                name="period"
                inputsEnabled={inputsEnabled}
                defaultValue={RecurringTaskPeriod.WEEKLY}
              />
              <FieldError actionResult={actionData} fieldName="/period" />
            </FormControl>
          </Stack>
        </CardContent>
        <CardActions>
          <ButtonGroup>
            <Button
              id="journal-create"
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
  "/app/workspace/journals",
  ParamsSchema,
  {
    error: () => `There was an error creating the journal! Please try again!`,
  },
);
