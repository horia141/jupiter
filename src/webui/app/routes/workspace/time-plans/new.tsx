import { ApiError, RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
} from "@mui/material";
import { Stack } from "@mui/system";
import type { ActionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCard } from "~/components/infra/section-card";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

const CreateFormSchema = {
  rightNow: z.string(),
  period: z.nativeEnum(RecurringTaskPeriod),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await getLoggedInApiClient(session).timePlans.timePlanCreate(
      {
        right_now: form.rightNow,
        period: form.period,
      }
    );

    return redirect(`/workspace/time-plans/${result.new_time_plan.ref_id}`);
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

export default function NewTimePlan() {
  const transition = useTransition();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  return (
    <LeafPanel key={"time-plans"} returnLocation="/workspace/time-plans">
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="Properties"
        actions={[
          <Button
            key="add"
            id="time-plan-create"
            variant="contained"
            disabled={!inputsEnabled}
            type="submit"
            name="intent"
            value="create"
          >
            Create
          </Button>,
        ]}
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="rightNow" shrink margin="dense">
              The Date
            </InputLabel>
            <OutlinedInput
              type="date"
              label="rightNow"
              name="rightNow"
              readOnly={!inputsEnabled}
              defaultValue={DateTime.now().toISODate()}
            />

            <FieldError actionResult={actionData} fieldName="/right_now" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="period">Period</InputLabel>
            <Select
              labelId="status"
              name="period"
              readOnly={!inputsEnabled}
              defaultValue={RecurringTaskPeriod.DAILY}
              label="Period"
            >
              {Object.values(RecurringTaskPeriod).map((s) => (
                <MenuItem key={s} value={s}>
                  {periodName(s)}
                </MenuItem>
              ))}
            </Select>
            <FieldError actionResult={actionData} fieldName="/period" />
          </FormControl>
        </Stack>
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the time plan! Please try again!`
);
