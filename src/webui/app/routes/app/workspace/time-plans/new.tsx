import { ApiError, RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
} from "@mui/material";
import { Stack } from "@mui/system";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useActionData,
  useNavigation,
  useSearchParams,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseQuery } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { PeriodSelect } from "~/components/domain/core/period-select";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({});

const QuerySchema = z.object({
  initialRightNow: z.string().optional(),
  initialPeriod: z.nativeEnum(RecurringTaskPeriod).optional(),
});

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
    const result = await apiClient.timePlans.timePlanCreate({
      right_now: form.rightNow,
      period: form.period,
    });

    return redirect(`/app/workspace/time-plans/${result.new_time_plan.ref_id}`);
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
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const actionData = useActionData<typeof action>();
  const [queryRaw] = useSearchParams();
  const inputsEnabled = navigation.state === "idle";

  const query = parseQuery(queryRaw, QuerySchema);
  const initialRightNow =
    query.initialRightNow ||
    DateTime.local({
      zone: topLevelInfo.user.timezone,
    }).toISODate();
  const initialPeriod = query.initialPeriod || RecurringTaskPeriod.WEEKLY;

  return (
    <LeafPanel
      fakeKey={`time-plans-${initialRightNow}-${initialPeriod}/new`}
      returnLocation="/app/workspace/time-plans"
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <SectionCardNew
        title="Properties"
        actions={
          <SectionActions
            id="time-plan-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "time-plan-create",
                text: "Create",
                value: "create",
                disabled: !inputsEnabled,
                highlight: true,
              }),
            ]}
          />
        }
      >
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
              defaultValue={initialRightNow}
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
              defaultValue={initialPeriod}
            />
            <FieldError actionResult={actionData} fieldName="/period" />
          </FormControl>
        </Stack>
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/time-plans",
  ParamsSchema,
  {
    error: () => `There was an error creating the time plan! Please try again!`,
  },
);
