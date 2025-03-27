import type {
  RecurringTaskDueAtDay,
  RecurringTaskSkipRule,
} from "@jupiter/webapi-client";
import { Difficulty, Eisen, RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  FormControl,
  FormLabel,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import type { SomeErrorNoData } from "~/logic/action-result";
import { periodName } from "~/logic/domain/period";
import { DifficultySelect } from "./difficulty-select";
import { EisenhowerSelect } from "./eisenhower-select";
import { FieldError } from "./infra/errors";

import { useEffect, useState } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";
import { RecurringTaskSkipRuleBlock } from "./recurring-task-skip-rule-block";

interface RecurringTaskGenParamsBlockProps {
  inputsEnabled: boolean;
  namePrefix?: string;
  fieldsPrefix?: string;
  allowNonePeriod?: boolean;
  allowSkipRule?: boolean;
  period: RecurringTaskPeriod | "none";
  onChangePeriod?: (period: RecurringTaskPeriod | "none") => void;
  eisen?: Eisen | null;
  difficulty?: Difficulty | null;
  actionableFromDay?: RecurringTaskDueAtDay | null;
  actionableFromMonth?: RecurringTaskDueAtDay | null;
  dueAtDay?: RecurringTaskDueAtDay | null;
  dueAtMonth?: RecurringTaskDueAtDay | null;
  skipRule?: RecurringTaskSkipRule | null;
  actionData?: SomeErrorNoData;
}

export function RecurringTaskGenParamsBlock(
  props: RecurringTaskGenParamsBlockProps,
) {
  const isBigScreen = useBigScreen();
  const [period, setPeriod] = useState(props.period);
  useEffect(() => {
    setPeriod(props.period);
  }, [props.period]);

  const [showParams, setShowParams] = useState(
    !(props.allowNonePeriod === true && props.period === "none"),
  );
  useEffect(() => {
    setShowParams(!(props.allowNonePeriod === true && props.period === "none"));
  }, [props.allowNonePeriod, props.period]);

  function handleChangePeriod(
    event: React.MouseEvent<HTMLElement>,
    newPeriod: RecurringTaskPeriod | "none" | null,
  ) {
    if (newPeriod === null) {
      return;
    }
    if (newPeriod === "none") {
      setShowParams(false);
    } else {
      setShowParams(true);
    }
    setPeriod(newPeriod);
    if (props.onChangePeriod) {
      props.onChangePeriod(newPeriod);
    }
  }

  return (
    <>
      <FormControl fullWidth>
        <FormLabel id="period">Period</FormLabel>
        <ToggleButtonGroup
          value={period}
          exclusive
          fullWidth
          onChange={handleChangePeriod}
        >
          {props.allowNonePeriod && (
            <ToggleButton value="none" disabled={!props.inputsEnabled}>
              None
            </ToggleButton>
          )}
          {Object.values(RecurringTaskPeriod).map((s) => (
            <ToggleButton key={s} value={s} disabled={!props.inputsEnabled}>
              {periodName(s, isBigScreen)}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
        <input
          type="hidden"
          name={constructFieldName(props.namePrefix, "period")}
          value={period}
        />
        <FieldError
          actionResult={props.actionData}
          fieldName={constructFieldErrorName(props.fieldsPrefix, "status")}
        />
      </FormControl>

      {showParams && (
        <>
          <FormControl fullWidth>
            <FormLabel id="eisen">Eisenhower</FormLabel>
            <EisenhowerSelect
              name={constructFieldName(props.namePrefix, "eisen")}
              defaultValue={props.eisen || Eisen.REGULAR}
              inputsEnabled={props.inputsEnabled}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName={constructFieldErrorName(props.fieldsPrefix, "eisen")}
            />
          </FormControl>

          <FormControl fullWidth>
            <FormLabel id="difficulty">Difficulty</FormLabel>
            <DifficultySelect
              name={constructFieldName(props.namePrefix, "difficulty")}
              defaultValue={props.difficulty || Difficulty.EASY}
              inputsEnabled={props.inputsEnabled}
            />
            <FieldError
              actionResult={props.actionData}
              fieldName={constructFieldErrorName(
                props.fieldsPrefix,
                "difficulty",
              )}
            />
          </FormControl>

          {period === RecurringTaskPeriod.DAILY && <> </>}

          {period === RecurringTaskPeriod.WEEKLY && (
            <>
              <Stack spacing={2} useFlexGap direction="row">
                <FormControl fullWidth>
                  <InputLabel id="actionableFromDay">
                    Actionable From Day [Optional]
                  </InputLabel>
                  <Select
                    label="Actionable From Day"
                    name={constructFieldName(
                      props.namePrefix,
                      "actionableFromDay",
                    )}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.actionableFromDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    <MenuItem value={1}>1</MenuItem>
                    <MenuItem value={2}>2</MenuItem>
                    <MenuItem value={3}>3</MenuItem>
                    <MenuItem value={4}>4</MenuItem>
                    <MenuItem value={5}>5</MenuItem>
                    <MenuItem value={6}>6</MenuItem>
                    <MenuItem value={7}>7</MenuItem>
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "actionable_from_day",
                    )}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="dueAtDay">Due At Day [Optional]</InputLabel>
                  <Select
                    label="Due At Day"
                    name={constructFieldName(props.namePrefix, "dueAtDay")}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.dueAtDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    <MenuItem value={1}>1</MenuItem>
                    <MenuItem value={2}>2</MenuItem>
                    <MenuItem value={3}>3</MenuItem>
                    <MenuItem value={4}>4</MenuItem>
                    <MenuItem value={5}>5</MenuItem>
                    <MenuItem value={6}>6</MenuItem>
                    <MenuItem value={7}>7</MenuItem>
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "due_at_day",
                    )}
                  />
                </FormControl>
              </Stack>
            </>
          )}

          {period === RecurringTaskPeriod.MONTHLY && (
            <>
              <Stack spacing={2} useFlexGap direction="row">
                <FormControl fullWidth>
                  <InputLabel id="actionableFromDay">
                    Actionable From Day [Optional]
                  </InputLabel>
                  <Select
                    label="Actionable From Day"
                    name={constructFieldName(
                      props.namePrefix,
                      "actionableFromDay",
                    )}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.actionableFromDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {Array.from({ length: 31 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {i + 1}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "actionable_from_day",
                    )}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="dueAtDay">Due At Day [Optional]</InputLabel>
                  <Select
                    label="Due At Day"
                    name={constructFieldName(props.namePrefix, "dueAtDay")}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.dueAtDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {Array.from({ length: 31 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {i + 1}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "due_at_day",
                    )}
                  />
                </FormControl>
              </Stack>
            </>
          )}

          {period === RecurringTaskPeriod.QUARTERLY && (
            <>
              <Stack spacing={2} useFlexGap direction="row">
                <FormControl fullWidth>
                  <InputLabel id="actionableFromDay">
                    Actionable From Day [Optional]
                  </InputLabel>
                  <Select
                    label="Actionable From Day"
                    name={constructFieldName(
                      props.namePrefix,
                      "actionableFromDay",
                    )}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.actionableFromDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {Array.from({ length: 31 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {i + 1}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "actionable_from_day",
                    )}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="actionableFromMonth">
                    Actionable From Month [Optional]
                  </InputLabel>
                  <Select
                    label="Actionable From Month"
                    name={constructFieldName(
                      props.namePrefix,
                      "actionableFromMonth",
                    )}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.actionableFromMonth || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    <MenuItem value={1}>1 : Jan / Apr / Jul / Oct</MenuItem>
                    <MenuItem value={2}>2 : Feb / May / Aug / Nov</MenuItem>
                    <MenuItem value={3}>3 : Mar / Jun / Sep / Dec</MenuItem>
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "actionable_from_month",
                    )}
                  />
                </FormControl>
              </Stack>

              <Stack spacing={2} useFlexGap direction="row">
                <FormControl fullWidth>
                  <InputLabel id="dueAtDay">Due At Day [Optional]</InputLabel>
                  <Select
                    label="Due At Day"
                    name={constructFieldName(props.namePrefix, "dueAtDay")}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.dueAtDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {Array.from({ length: 31 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {i + 1}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "due_at_day",
                    )}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="dueAtMonth">
                    Due At Month [Optional]
                  </InputLabel>
                  <Select
                    label="Due At Month"
                    name={constructFieldName(props.namePrefix, "dueAtMonth")}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.dueAtMonth || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    <MenuItem value={1}>1 : Jan / Apr / Jul / Oct</MenuItem>
                    <MenuItem value={2}>2 : Feb / May / Aug / Nov</MenuItem>
                    <MenuItem value={3}>3 : Mar / Jun / Sep / Dec</MenuItem>
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "due_at_month",
                    )}
                  />
                </FormControl>
              </Stack>
            </>
          )}

          {period === RecurringTaskPeriod.YEARLY && (
            <>
              <Stack spacing={2} useFlexGap direction="row">
                <FormControl fullWidth>
                  <InputLabel id="actionableFromDay">
                    Actionable From Day [Optional]
                  </InputLabel>
                  <Select
                    label="Actionable From Day"
                    name={constructFieldName(
                      props.namePrefix,
                      "actionableFromDay",
                    )}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.actionableFromDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {Array.from({ length: 31 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {i + 1}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "actionable_from_day",
                    )}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="actionableFromMonth">
                    Actionable From Month [Optional]
                  </InputLabel>
                  <Select
                    label="Actionable From Month"
                    name={constructFieldName(
                      props.namePrefix,
                      "actionableFromMonth",
                    )}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.actionableFromMonth || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {[
                      "Jan",
                      "Feb",
                      "Mar",
                      "Apr",
                      "May",
                      "Jun",
                      "Jul",
                      "Aug",
                      "Sep",
                      "Oct",
                      "Nov",
                      "Dec",
                    ].map((month, index) => (
                      <MenuItem key={index + 1} value={index + 1}>
                        {month}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "actionable_from_month",
                    )}
                  />
                </FormControl>
              </Stack>

              <Stack spacing={2} useFlexGap direction="row">
                <FormControl fullWidth>
                  <InputLabel id="dueAtDay">Due At Day [Optional]</InputLabel>
                  <Select
                    label="Due At Day"
                    name={constructFieldName(props.namePrefix, "dueAtDay")}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.dueAtDay || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {Array.from({ length: 31 }, (_, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {i + 1}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "due_at_day",
                    )}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="dueAtMonth">
                    Due At Month [Optional]
                  </InputLabel>
                  <Select
                    label="Due At Month"
                    name={constructFieldName(props.namePrefix, "dueAtMonth")}
                    readOnly={!props.inputsEnabled}
                    defaultValue={props.dueAtMonth || ""}
                  >
                    <MenuItem value={""}>N/A</MenuItem>
                    {[
                      "Jan",
                      "Feb",
                      "Mar",
                      "Apr",
                      "May",
                      "Jun",
                      "Jul",
                      "Aug",
                      "Sep",
                      "Oct",
                      "Nov",
                      "Dec",
                    ].map((month, index) => (
                      <MenuItem key={index + 1} value={index + 1}>
                        {month}
                      </MenuItem>
                    ))}
                  </Select>
                  <FieldError
                    actionResult={props.actionData}
                    fieldName={constructFieldErrorName(
                      props.fieldsPrefix,
                      "due_at_month",
                    )}
                  />
                </FormControl>
              </Stack>
            </>
          )}

          {props.allowSkipRule && (
            <>
              <FormControl fullWidth>
                <RecurringTaskSkipRuleBlock
                  inputsEnabled={props.inputsEnabled}
                  name={constructFieldName(props.namePrefix, "skipRule")}
                  period={period as RecurringTaskPeriod}
                  skipRule={props.skipRule}
                />
                <FieldError
                  actionResult={props.actionData}
                  fieldName={constructFieldErrorName(
                    props.fieldsPrefix,
                    "skip_rule",
                  )}
                />
              </FormControl>
            </>
          )}
        </>
      )}
    </>
  );
}

function constructFieldName(
  namePrefix: string | undefined,
  fieldName: string,
): string {
  if (!namePrefix) {
    return fieldName;
  }
  return `${namePrefix}${
    fieldName.charAt(0).toUpperCase() + fieldName.slice(1)
  }`;
}

function constructFieldErrorName(
  fieldsPrefix: string | undefined,
  fieldName: string,
): string {
  if (!fieldsPrefix) {
    return `/${fieldName}`;
  }
  return `/${fieldsPrefix}_${fieldName}`;
}
