import {
  ApiError,
  Difficulty,
  Eisen,
  PersonRelationship,
  RecurringTaskPeriod,
} from "@jupiter/webapi-client";
import type { SelectChangeEvent } from "@mui/material";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
} from "@mui/material";
import type { ActionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useState } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { difficultyName } from "~/logic/domain/difficulty";
import { eisenName } from "~/logic/domain/eisen";
import { periodName } from "~/logic/domain/period";
import { birthdayFromParts } from "~/logic/domain/person-birthday";
import { personRelationshipName } from "~/logic/domain/person-relationship";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

const CreateFormSchema = {
  name: z.string(),
  relationship: z.string(),
  birthdayDay: z.string(),
  birthdayMonth: z.string(),
  catchUpPeriod: z.string(),
  catchUpEisen: z.string().optional(),
  catchUpDifficulty: z.string().optional(),
  catchUpActionableFromDay: z.string().optional(),
  catchUpActionableFromMonth: z.string().optional(),
  catchUpDueAtDay: z.string().optional(),
  catchUpDueAtMonth: z.string().optional(),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.persons.personCreate({
      name: form.name,
      relationship: form.relationship as PersonRelationship,
      catch_up_period:
        form.catchUpPeriod === "none"
          ? undefined
          : (form.catchUpPeriod as RecurringTaskPeriod),
      catch_up_eisen:
        form.catchUpPeriod === "none"
          ? undefined
          : form.catchUpEisen === "default"
          ? undefined
          : (form.catchUpEisen as Eisen),
      catch_up_difficulty:
        form.catchUpPeriod === "none"
          ? undefined
          : form.catchUpDifficulty === "default"
          ? undefined
          : (form.catchUpDifficulty as Difficulty),
      catch_up_actionable_from_day:
        form.catchUpPeriod === "none"
          ? undefined
          : form.catchUpActionableFromDay === undefined ||
            form.catchUpActionableFromDay === ""
          ? undefined
          : parseInt(form.catchUpActionableFromDay),
      catch_up_actionable_from_month:
        form.catchUpPeriod === "none"
          ? undefined
          : form.catchUpActionableFromMonth === undefined ||
            form.catchUpActionableFromMonth === ""
          ? undefined
          : parseInt(form.catchUpActionableFromMonth),
      catch_up_due_at_day:
        form.catchUpPeriod === "none"
          ? undefined
          : form.catchUpDueAtDay === undefined || form.catchUpDueAtDay === ""
          ? undefined
          : parseInt(form.catchUpDueAtDay),
      catch_up_due_at_month:
        form.catchUpPeriod === "none"
          ? undefined
          : form.catchUpDueAtMonth === undefined ||
            form.catchUpDueAtMonth === ""
          ? undefined
          : parseInt(form.catchUpDueAtMonth),
      birthday:
        form.birthdayDay === "N/A" || form.birthdayMonth === "N/A"
          ? undefined
          : birthdayFromParts(
              parseInt(form.birthdayDay),
              parseInt(form.birthdayMonth)
            ),
    });

    return redirect(`/workspace/persons/${result.new_person.ref_id}`);
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

export default function NewPerson() {
  const transition = useTransition();
  const actionData = useActionData<typeof action>();

  const inputsEnabled = transition.state === "idle";

  const [showCatchUpParams, setShowCatchUpParams] = useState(false);

  function handleChangeCatchUpPeriod(event: SelectChangeEvent) {
    if (event.target.value === "none") {
      setShowCatchUpParams(false);
    } else {
      setShowCatchUpParams(true);
    }
  }

  return (
    <LeafPanel key={"persons/new"} returnLocation="/workspace/persons">
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
              <InputLabel id="relationship">Relationship</InputLabel>
              <Select
                labelId="relationship"
                name="relationship"
                readOnly={!inputsEnabled}
                defaultValue={PersonRelationship.FAMILY}
                label="Relationship"
              >
                {Object.values(PersonRelationship).map((relationship) => (
                  <MenuItem key={relationship} value={relationship}>
                    {personRelationshipName(relationship)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={actionData} fieldName="/relationship" />
            </FormControl>

            <Stack spacing={2} useFlexGap direction="row">
              <FormControl fullWidth>
                <InputLabel id="birthdayDay">Birthday Day</InputLabel>
                <Select
                  labelId="birthdayDay"
                  name="birthdayDay"
                  readOnly={!inputsEnabled}
                  defaultValue={"N/A"}
                  label="Birthday Day"
                >
                  <MenuItem value={"N/A"}>N/A</MenuItem>
                  <MenuItem value={1}>1st</MenuItem>
                  <MenuItem value={2}>2nd</MenuItem>
                  <MenuItem value={3}>3rd</MenuItem>
                  <MenuItem value={4}>4th</MenuItem>
                  <MenuItem value={5}>5th</MenuItem>
                  <MenuItem value={6}>6th</MenuItem>
                  <MenuItem value={7}>7th</MenuItem>
                  <MenuItem value={8}>8th</MenuItem>
                  <MenuItem value={9}>9th</MenuItem>
                  <MenuItem value={10}>10th</MenuItem>
                  <MenuItem value={11}>11th</MenuItem>
                  <MenuItem value={12}>12th</MenuItem>
                  <MenuItem value={13}>13th</MenuItem>
                  <MenuItem value={14}>14th</MenuItem>
                  <MenuItem value={15}>15th</MenuItem>
                  <MenuItem value={16}>16th</MenuItem>
                  <MenuItem value={17}>17th</MenuItem>
                  <MenuItem value={18}>18th</MenuItem>
                  <MenuItem value={19}>19th</MenuItem>
                  <MenuItem value={20}>20th</MenuItem>
                  <MenuItem value={21}>21st</MenuItem>
                  <MenuItem value={22}>22nd</MenuItem>
                  <MenuItem value={23}>23rd</MenuItem>
                  <MenuItem value={24}>24th</MenuItem>
                  <MenuItem value={25}>25th</MenuItem>
                  <MenuItem value={26}>26th</MenuItem>
                  <MenuItem value={27}>27th</MenuItem>
                  <MenuItem value={28}>28th</MenuItem>
                  <MenuItem value={29}>29th</MenuItem>
                  <MenuItem value={30}>30th</MenuItem>
                  <MenuItem value={31}>31st</MenuItem>
                </Select>

                <FieldError actionResult={actionData} fieldName="/birthday" />
              </FormControl>

              <FormControl fullWidth>
                <InputLabel id="birthdayMonth">Birthday Month</InputLabel>
                <Select
                  labelId="birthdayMonth"
                  name="birthdayMonth"
                  readOnly={!inputsEnabled}
                  defaultValue={"N/A"}
                  label="Birthday Month"
                >
                  <MenuItem value={"N/A"}>N/A</MenuItem>
                  <MenuItem value={1}>January</MenuItem>
                  <MenuItem value={2}>February</MenuItem>
                  <MenuItem value={3}>March</MenuItem>
                  <MenuItem value={4}>April</MenuItem>
                  <MenuItem value={5}>May</MenuItem>
                  <MenuItem value={6}>June</MenuItem>
                  <MenuItem value={7}>July</MenuItem>
                  <MenuItem value={8}>August</MenuItem>
                  <MenuItem value={9}>September</MenuItem>
                  <MenuItem value={10}>October</MenuItem>
                  <MenuItem value={11}>November</MenuItem>
                  <MenuItem value={12}>December</MenuItem>
                </Select>
                <FieldError actionResult={actionData} fieldName="/birthday" />
              </FormControl>
            </Stack>

            <Divider>Catch Up</Divider>

            <FormControl fullWidth>
              <InputLabel id="catchUpPeriod">Catch Up Period</InputLabel>
              <Select
                labelId="catchUpPeriod"
                name="catchUpPeriod"
                readOnly={!inputsEnabled}
                onChange={handleChangeCatchUpPeriod}
                defaultValue={"none"}
                label="Catch Up Period"
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
                fieldName="/catch_up_period"
              />
            </FormControl>

            {showCatchUpParams && (
              <>
                <FormControl fullWidth>
                  <InputLabel id="catchUpEisen">Eisenhower</InputLabel>
                  <Select
                    labelId="catchUpEisen"
                    name="catchUpEisen"
                    readOnly={!inputsEnabled}
                    defaultValue={"default"}
                    label="Eisenhower"
                  >
                    <MenuItem value="default">Default</MenuItem>
                    {Object.values(Eisen).map((e) => (
                      <MenuItem key={e} value={e}>
                        {eisenName(e)}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={actionData}
                    fieldName="/catch_up_eisen"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="catchUpDifficulty">Difficulty</InputLabel>
                  <Select
                    labelId="catchUpDifficulty"
                    name="catchUpDifficulty"
                    readOnly={!inputsEnabled}
                    defaultValue={"default"}
                    label="Difficulty"
                  >
                    <MenuItem value="default">Default</MenuItem>
                    {Object.values(Difficulty).map((e) => (
                      <MenuItem key={e} value={e}>
                        {difficultyName(e)}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={actionData}
                    fieldName="/catch_up_difficulty"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="catchUpActionableFromDay">
                    Actionable From Day
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Actionable From Day"
                    name="catchUpActionableFromDay"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/catch_up_actionable_from_day"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="catchUpActionableFromMonth">
                    Actionable From Month
                  </InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Actionable From Month"
                    name="catchUpActionableFromMonth"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/catch_up_actionable_from_month"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="catchUpDueAtDay">Due At Day</InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Due At Day"
                    name="catchUpDueAtDay"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/catch_up_due_at_day"
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="catchUpDueAtMonth">Due At Month</InputLabel>
                  <OutlinedInput
                    type="number"
                    label="Due At Month"
                    name="catchUpDueAtMonth"
                    readOnly={!inputsEnabled}
                    defaultValue={""}
                  />
                  <FieldError
                    actionResult={actionData}
                    fieldName="/catch_up_due_at_month"
                  />
                </FormControl>
              </>
            )}
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              id="person-create"
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error creating the person! Please try again!`
);
