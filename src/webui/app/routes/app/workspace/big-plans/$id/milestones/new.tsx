import { ApiError } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation, useParams } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCard } from "~/components/infra/section-card";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import {
  aGlobalError,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { DateInputWithSuggestions } from "~/components/domain/core/date-input-with-suggestions";
import { getSuggestedDatesForBigPlanMilestoneDate } from "~/logic/domain/suggested-date";

const ParamsSchema = z.object({
  id: z.string(),
});

const CreateFormSchema = z.object({
  name: z.string(),
  date: z.string(),
});

export const handle = {
  displayType: DisplayType.LEAFLET,
};

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  console.log("action");
  const { id: bigPlanId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.milestones.bigPlanMilestoneCreate({
      big_plan_ref_id: bigPlanId,
      date: form.date,
      name: form.name,
    });

    return redirect(
      `/app/workspace/big-plans/${bigPlanId}/milestones/${result.new_big_plan_milestone.ref_id}`,
    );
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

export default function BigPlanMilestoneNew() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const { id: bigPlanId } = useParams();

  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      isLeaflet
      fakeKey="big-plan-milestones/new"
      returnLocation={`/app/workspace/big-plans/${bigPlanId}`}
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        id="big-plan-milestone-properties"
        title="Properties"
        actions={
          <SectionActions
            id="big-plan-milestone-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Create",
                value: "create",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput label="Name" name="name" readOnly={!inputsEnabled} />
            <FieldError actionResult={actionData} fieldName="/name" />
          </FormControl>

          <FormControl fullWidth>
            <InputLabel id="date" shrink margin="dense">
              Date
            </InputLabel>
            <DateInputWithSuggestions
              name="date"
              label="date"
              inputsEnabled={inputsEnabled}
              defaultValue={topLevelInfo.today}
              suggestedDates={getSuggestedDatesForBigPlanMilestoneDate(
                topLevelInfo.today,
              )}
            />
            <FieldError actionResult={actionData} fieldName="/date" />
          </FormControl>
        </Stack>
      </SectionCard>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary("../..", ParamsSchema, {
  error: () => `There was an error creating the milestone! Please try again!`,
});
