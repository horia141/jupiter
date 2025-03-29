import {
  ApiError,
  Difficulty,
  Eisen,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import type { SelectChangeEvent } from "@mui/material";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormLabel,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
} from "@mui/material";

import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useState } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { DifficultySelect } from "~/components/difficulty-select";
import { EisenhowerSelect } from "~/components/eisenhower-select";
import { IconSelector } from "~/components/icon-selector";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";

import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { StandardDivider } from "~/components/standard-divider";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

const CreateFormSchema = {
  name: z.string(),
  icon: z.string().optional(),
  collectionPeriod: z.union([
    z.nativeEnum(RecurringTaskPeriod),
    z.literal("none"),
  ]),
  collectionEisen: z.nativeEnum(Eisen).optional(),
  collectionDifficulty: z.nativeEnum(Difficulty).optional(),
  collectionActionableFromDay: z.string().optional(),
  collectionActionableFromMonth: z.string().optional(),
  collectionDueAtDay: z.string().optional(),
  collectionDueAtMonth: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.metrics.metricCreate({
      name: form.name,
      icon: form.icon,
      collection_period:
        form.collectionPeriod === "none"
          ? undefined
          : (form.collectionPeriod as RecurringTaskPeriod),
      collection_eisen:
        form.collectionPeriod === "none"
          ? undefined
          : (form.collectionEisen as Eisen),
      collection_difficulty:
        form.collectionPeriod === "none"
          ? undefined
          : (form.collectionDifficulty as Difficulty),
      collection_actionable_from_day:
        form.collectionPeriod === "none"
          ? undefined
          : form.collectionActionableFromDay === undefined ||
              form.collectionActionableFromDay === ""
            ? undefined
            : parseInt(form.collectionActionableFromDay),
      collection_actionable_from_month:
        form.collectionPeriod === "none"
          ? undefined
          : form.collectionActionableFromMonth === undefined ||
              form.collectionActionableFromMonth === ""
            ? undefined
            : parseInt(form.collectionActionableFromMonth),
      collection_due_at_day:
        form.collectionPeriod === "none"
          ? undefined
          : form.collectionDueAtDay === undefined ||
              form.collectionDueAtDay === ""
            ? undefined
            : parseInt(form.collectionDueAtDay),
      collection_due_at_month:
        form.collectionPeriod === "none"
          ? undefined
          : form.collectionDueAtMonth === undefined ||
              form.collectionDueAtMonth === ""
            ? undefined
            : parseInt(form.collectionDueAtMonth),
    });

    return redirect(`/app/workspace/metrics/${result.new_metric.ref_id}`);
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

export default function NewMetric() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "idle";

  const [showCollectionParams, setShowCollectionParams] = useState(false);

  function handleChangeCollectionPeriod(event: SelectChangeEvent) {
    if (event.target.value === "none") {
      setShowCollectionParams(false);
    } else {
      setShowCollectionParams(true);
    }
  }

  return (
    <LeafPanel
      key={"metrics/new"}
      returnLocation="/app/workspace/metrics"
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
              <InputLabel id="icon">Icon</InputLabel>
              <IconSelector readOnly={!inputsEnabled} />
              <FieldError actionResult={actionData} fieldName="/icon" />
            </FormControl>

            <StandardDivider title="Collection" size="large" />

            <FormControl fullWidth>
              <InputLabel id="collectionPeriod">Collection Period</InputLabel>
              <Select
                labelId="collectionPeriod"
                name="collectionPeriod"
                readOnly={!inputsEnabled}
                onChange={handleChangeCollectionPeriod}
                defaultValue={"none"}
                label="Collection Period"
              >
                <MenuItem value={"none"}>None</MenuItem>
                {Object.values(RecurringTaskPeriod).map((period) => (
                  <MenuItem key={period} value={period}>
                    {periodName(period)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={actionData}
                fieldName="/collection_period"
              />
            </FormControl>

            {showCollectionParams && (
              <>
                <FormControl fullWidth>
                  <FormLabel id="collectionEisen">Eisenhower</FormLabel>
                  <EisenhowerSelect
                    name="collectionEisen"
                    defaultValue={Eisen.REGULAR}
                    inputsEnabled={inputsEnabled}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_eisen"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <FormLabel id="collectionDifficulty">Difficulty</FormLabel>
                  <DifficultySelect
                    name="collectionDifficulty"
                    defaultValue={Difficulty.EASY}
                    inputsEnabled={inputsEnabled}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_difficulty"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionActionableFromDay">
                    Actionable From Day [Optional]
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Actionable From Day"
                    name="collectionActionableFromDay"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_actionable_from_day"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionActionableFromMonth">
                    Actionable From Month [Optional]
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Actionable From Month"
                    name="collectionActionableFromMonth"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_actionable_from_month"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionDueAtDay">
                    Due At Day [Optional]
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Due At Day"
                    name="collectionDueAtDay"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_due_at_day"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="collectionDueAtMonth">
                    Due At Month [Optional]
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Due At Month"
                    name="collectionDueAtMonth"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/collection_due_at_month"
                  />
                </FormControl>
              </>
            )}
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="metric-create"
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

export const ErrorBoundary = makeLeafErrorBoundary(`/app/workspace/metrics`, {
  error: () => `There was an error creating the metric! Please try again!`,
});
