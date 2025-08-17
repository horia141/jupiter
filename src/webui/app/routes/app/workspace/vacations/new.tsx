import { ApiError } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput } from "@mui/material";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { useContext } from "react";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { ActionsPosition, SectionCard } from "~/components/infra/section-card";
import {
  SectionActions,
  ActionSingle,
} from "~/components/infra/section-actions";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

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
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key="vacations/new"
      fakeKey={"vacations/new"}
      returnLocation="/app/workspace/vacations"
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      <SectionCard
        title="Properties"
        actionsPosition={ActionsPosition.BELOW}
        actions={
          <SectionActions
            id="vacation-properties"
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
        <FormControl fullWidth>
          <InputLabel id="name">Name</InputLabel>
          <OutlinedInput label="Name" name="name" readOnly={!inputsEnabled} />
          <FieldError actionResult={actionData} fieldName="/name" />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="startDate" shrink>
            Start Date
          </InputLabel>
          <OutlinedInput
            type="date"
            notched
            label="startDate"
            name="startDate"
            readOnly={!inputsEnabled}
            disabled={!inputsEnabled}
          />
          <FieldError actionResult={actionData} fieldName="/start_date" />
        </FormControl>

        <FormControl fullWidth>
          <InputLabel id="endDate" shrink>
            End Date
          </InputLabel>
          <OutlinedInput
            type="date"
            notched
            label="endDate"
            name="endDate"
            readOnly={!inputsEnabled}
            disabled={!inputsEnabled}
          />
          <FieldError actionResult={actionData} fieldName="/end_date" />
        </FormControl>
      </SectionCard>
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
