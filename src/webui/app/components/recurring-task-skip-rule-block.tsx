import type { RecurringTaskSkipRule } from "@jupiter/webapi-client";
import { RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { DateTime } from "luxon";
import { useEffect, useState } from "react";
import type { SkipRule } from "~/logic/domain/recurring-task-skip-rule";
import {
  assembleSkipRule,
  isCompatibleWithPeriod,
  parseSkipRule,
  SkipRuleType,
  skipRuleTypeName,
} from "~/logic/domain/recurring-task-skip-rule";
import { useBigScreen } from "~/rendering/use-big-screen";

interface RecurringTaskSkipRuleBlockProps {
  inputsEnabled: boolean;
  name: string;
  period: RecurringTaskPeriod;
  skipRule?: RecurringTaskSkipRule | null;
}

interface EditingInfo {
  theType: SkipRuleType;
  n: string;
  k: string;
  daysRelWeek: number[];
  daysRelMonth: number[];
  weeks: number[];
  months: number[];
  quarters: number[];
}

function skipRuleToEditingInfo(
  period: RecurringTaskPeriod,
  skipRule: SkipRule,
): EditingInfo {
  if (!isCompatibleWithPeriod(skipRule.type, period)) {
    return {
      theType: SkipRuleType.NONE,
      n: "3",
      k: "0",
      daysRelWeek: [1],
      daysRelMonth: [1],
      weeks: [1],
      months: [1],
      quarters: [1],
    };
  }

  return {
    theType: skipRule.type,
    n: "n" in skipRule ? skipRule.n.toString() : "3",
    k: "k" in skipRule ? skipRule.k.toString() : "0",
    daysRelWeek: "daysRelWeek" in skipRule ? skipRule.daysRelWeek : [1],
    daysRelMonth: "daysRelMonth" in skipRule ? skipRule.daysRelMonth : [1],
    weeks: "weeks" in skipRule ? skipRule.weeks : [1],
    months: "months" in skipRule ? skipRule.months : [1],
    quarters: "quarters" in skipRule ? skipRule.quarters : [1],
  };
}

function editingInfoToSkipRule(editingInfo: EditingInfo): SkipRule {
  switch (editingInfo.theType) {
    case SkipRuleType.NONE:
      return { type: SkipRuleType.NONE };
    case SkipRuleType.EVEN:
      return { type: SkipRuleType.EVEN };
    case SkipRuleType.ODD:
      return { type: SkipRuleType.ODD };
    case SkipRuleType.EVERY:
      const realN = parseInt(editingInfo.n);
      const realK = parseInt(editingInfo.k);
      if (isNaN(realN) || isNaN(realK)) {
        return { type: SkipRuleType.EVERY, n: -1, k: -1 };
      }
      return { type: SkipRuleType.EVERY, n: realN, k: realK };
    case SkipRuleType.CUSTOM_DAILY_REL_WEEKLY:
      return {
        type: SkipRuleType.CUSTOM_DAILY_REL_WEEKLY,
        daysRelWeek: editingInfo.daysRelWeek,
      };
    case SkipRuleType.CUSTOM_DAILY_REL_MONTHLY:
      return {
        type: SkipRuleType.CUSTOM_DAILY_REL_MONTHLY,
        daysRelMonth: editingInfo.daysRelMonth,
      };
    case SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY:
      return {
        type: SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY,
        weeks: editingInfo.weeks,
      };
    case SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY:
      return {
        type: SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY,
        months: editingInfo.months,
      };
    case SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY:
      return {
        type: SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY,
        quarters: editingInfo.quarters,
      };
  }
}

export function RecurringTaskSkipRuleBlock(
  props: RecurringTaskSkipRuleBlockProps,
) {
  const isBigScreen = useBigScreen();
  const [editingInfo, setEditingInfo] = useState<EditingInfo>(
    skipRuleToEditingInfo(props.period, parseSkipRule(props.skipRule)),
  );
  useEffect(() => {
    setEditingInfo(
      skipRuleToEditingInfo(props.period, parseSkipRule(props.skipRule)),
    );
  }, [props.skipRule, props.period]);

  function handleNewSkipRule(
    event: React.MouseEvent<HTMLElement>,
    newSkipRuleType: SkipRuleType | null,
  ) {
    if (newSkipRuleType === null) {
      return;
    }
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      theType: newSkipRuleType,
    }));
  }

  function handleChangeEveryNewN(newN: string) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      n: newN,
    }));
  }

  function handleChangeEveryNewK(newK: string) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      k: newK,
    }));
  }

  function handleChangeCustomDailyRelWeekly(day: number, include: boolean) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      daysRelWeek: include
        ? [...oldEditingInfo.daysRelWeek, day]
        : oldEditingInfo.daysRelWeek.filter((d) => d !== day),
    }));
  }

  function handleChangeCustomDailyRelMonthly(day: number, include: boolean) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      daysRelMonth: include
        ? [...oldEditingInfo.daysRelMonth, day]
        : oldEditingInfo.daysRelMonth.filter((d) => d !== day),
    }));
  }

  function handleChangeCustomWeeklyRelYearly(week: number, include: boolean) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      weeks: include
        ? [...oldEditingInfo.weeks, week]
        : oldEditingInfo.weeks.filter((w) => w !== week),
    }));
  }

  function handleChangeCustomMonthlyRelYearly(month: number, include: boolean) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      months: include
        ? [...oldEditingInfo.months, month]
        : oldEditingInfo.months.filter((m) => m !== month),
    }));
  }

  function handleChangeCustomQuarterlyRelYearly(
    quarter: number,
    include: boolean,
  ) {
    setEditingInfo((oldEditingInfo: EditingInfo) => ({
      ...oldEditingInfo,
      quarters: include
        ? [...oldEditingInfo.quarters, quarter]
        : oldEditingInfo.quarters.filter((q) => q !== quarter),
    }));
  }

  const everyBlock = (
    <>
      {editingInfo.theType === SkipRuleType.EVERY && (
        <Stack spacing={2} useFlexGap direction="row">
          <FormControl fullWidth>
            <InputLabel>Every N</InputLabel>
            <OutlinedInput
              label="Every N"
              readOnly={!props.inputsEnabled}
              value={editingInfo.n}
              onChange={(event) => handleChangeEveryNewN(event.target.value)}
            />
          </FormControl>
          <FormControl fullWidth>
            <InputLabel>Shift by K</InputLabel>
            <OutlinedInput
              label="Shift by K"
              readOnly={!props.inputsEnabled}
              value={editingInfo.k || ""}
              onChange={(event) => handleChangeEveryNewK(event.target.value)}
            />
          </FormControl>
        </Stack>
      )}
    </>
  );

  const customDailyRelWeeklyBlock = (
    <>
      {editingInfo.theType === SkipRuleType.CUSTOM_DAILY_REL_WEEKLY && (
        <Stack
          useFlexGap
          direction="row"
          sx={{ justifyContent: "space-around" }}
        >
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(1)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(1, checked)
            }
            label={isBigScreen ? "Mon" : "M"}
          />
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(2)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(2, checked)
            }
            label={isBigScreen ? "Tue" : "T"}
          />
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(3)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(3, checked)
            }
            label={isBigScreen ? "Wed" : "W"}
          />
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(4)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(4, checked)
            }
            label={isBigScreen ? "Thu" : "T"}
          />
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(5)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(5, checked)
            }
            label={isBigScreen ? "Fri" : "F"}
          />
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(6)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(6, checked)
            }
            label={isBigScreen ? "Sat" : "S"}
          />
          <FormControlLabel
            sx={{ marginRight: isBigScreen ? "8px" : "2px" }}
            control={<Checkbox size="small" />}
            checked={editingInfo.daysRelWeek.includes(7)}
            onChange={(event, checked) =>
              handleChangeCustomDailyRelWeekly(7, checked)
            }
            label={isBigScreen ? "Sun" : "S"}
          />
        </Stack>
      )}
    </>
  );

  const customDailyRelMonthlyBlock = (
    <>
      {editingInfo.theType === SkipRuleType.CUSTOM_DAILY_REL_MONTHLY && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          {[...Array(31).keys()].map((day) => (
            <FormControlLabel
              key={day}
              control={<Checkbox size="small" />}
              checked={editingInfo.daysRelMonth.includes(day + 1)}
              onChange={(event, checked) =>
                handleChangeCustomDailyRelMonthly(day + 1, checked)
              }
              label={day + 1}
            />
          ))}
        </Box>
      )}
    </>
  );

  const customWeeklyRelYearlyBlock = (
    <>
      {editingInfo.theType === SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          {[...Array(52).keys()].map((week) => (
            <FormControlLabel
              key={week}
              control={<Checkbox size="small" />}
              checked={editingInfo.weeks.includes(week + 1)}
              onChange={(event, checked) =>
                handleChangeCustomWeeklyRelYearly(week + 1, checked)
              }
              label={week + 1}
            />
          ))}
        </Box>
      )}
    </>
  );

  const customMonthlyRelYearlyBlock = (
    <>
      {editingInfo.theType === SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          {[...Array(12).keys()].map((month) => (
            <FormControlLabel
              key={month}
              control={<Checkbox size="small" />}
              checked={editingInfo.months.includes(month + 1)}
              onChange={(event, checked) =>
                handleChangeCustomMonthlyRelYearly(month + 1, checked)
              }
              label={DateTime.local()
                .set({ month: month + 1 })
                .toFormat("LLL")}
            />
          ))}
        </Box>
      )}
    </>
  );

  const customQuarterlyRelYearlyBlock = (
    <>
      {editingInfo.theType === SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY && (
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          {[...Array(4).keys()].map((quarter) => (
            <FormControlLabel
              key={quarter}
              control={<Checkbox size="small" />}
              checked={editingInfo.quarters.includes(quarter + 1)}
              onChange={(event, checked) =>
                handleChangeCustomQuarterlyRelYearly(quarter + 1, checked)
              }
              label={`Q${quarter + 1}`}
            />
          ))}
        </Box>
      )}
    </>
  );

  switch (props.period) {
    case RecurringTaskPeriod.DAILY:
      return (
        <Stack spacing={2} useFlexGap>
          <FormLabel id="period">Skip Rule</FormLabel>
          <ToggleButtonGroup
            value={editingInfo.theType}
            exclusive
            fullWidth
            onChange={handleNewSkipRule}
          >
            <ToggleButton
              size="small"
              value={SkipRuleType.NONE}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.NONE, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVEN}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVEN, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.ODD}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.ODD, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVERY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVERY, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.CUSTOM_DAILY_REL_WEEKLY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(
                SkipRuleType.CUSTOM_DAILY_REL_WEEKLY,
                isBigScreen,
              )}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.CUSTOM_DAILY_REL_MONTHLY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(
                SkipRuleType.CUSTOM_DAILY_REL_MONTHLY,
                isBigScreen,
              )}
            </ToggleButton>
          </ToggleButtonGroup>
          {everyBlock}
          {customDailyRelWeeklyBlock}
          {customDailyRelMonthlyBlock}
          <input
            type="hidden"
            name={props.name}
            value={assembleSkipRule(editingInfoToSkipRule(editingInfo))}
          />
        </Stack>
      );
    case RecurringTaskPeriod.WEEKLY:
      return (
        <Stack spacing={2} useFlexGap>
          <FormLabel id="period">Skip Rule</FormLabel>
          <ToggleButtonGroup
            value={editingInfo.theType}
            exclusive
            fullWidth
            onChange={handleNewSkipRule}
          >
            <ToggleButton
              size="small"
              value={SkipRuleType.NONE}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.NONE, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVEN}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVEN, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.ODD}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.ODD, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVERY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVERY, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(
                SkipRuleType.CUSTOM_WEEKLY_REL_YEARLY,
                isBigScreen,
              )}
            </ToggleButton>
          </ToggleButtonGroup>
          {everyBlock}
          {customWeeklyRelYearlyBlock}
          <input
            type="hidden"
            name={props.name}
            value={assembleSkipRule(editingInfoToSkipRule(editingInfo))}
          />
        </Stack>
      );
    case RecurringTaskPeriod.MONTHLY:
      return (
        <Stack spacing={2} useFlexGap>
          <FormLabel id="period">Skip Rule</FormLabel>
          <ToggleButtonGroup
            value={editingInfo.theType}
            exclusive
            fullWidth
            onChange={handleNewSkipRule}
          >
            <ToggleButton
              size="small"
              value={SkipRuleType.NONE}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.NONE, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVEN}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVEN, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.ODD}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.ODD, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVERY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVERY, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(
                SkipRuleType.CUSTOM_MONTHLY_REL_YEARLY,
                isBigScreen,
              )}
            </ToggleButton>
          </ToggleButtonGroup>
          {everyBlock}
          {customMonthlyRelYearlyBlock}
          <input
            type="hidden"
            name={props.name}
            value={assembleSkipRule(editingInfoToSkipRule(editingInfo))}
          />
        </Stack>
      );
    case RecurringTaskPeriod.QUARTERLY:
      return (
        <Stack spacing={2} useFlexGap>
          <FormLabel id="period">Skip Rule</FormLabel>
          <ToggleButtonGroup
            value={editingInfo.theType}
            exclusive
            fullWidth
            onChange={handleNewSkipRule}
          >
            <ToggleButton
              size="small"
              value={SkipRuleType.NONE}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.NONE, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVEN}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVEN, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.ODD}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.ODD, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVERY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVERY, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(
                SkipRuleType.CUSTOM_QUARTERLY_REL_YEARLY,
                isBigScreen,
              )}
            </ToggleButton>
          </ToggleButtonGroup>
          {everyBlock}
          {customQuarterlyRelYearlyBlock}
          <input
            type="hidden"
            name={props.name}
            value={assembleSkipRule(editingInfoToSkipRule(editingInfo))}
          />
        </Stack>
      );
    case RecurringTaskPeriod.YEARLY:
      return (
        <Stack spacing={2} useFlexGap>
          <FormLabel id="period">Skip Rule</FormLabel>
          <ToggleButtonGroup
            value={editingInfo.theType}
            exclusive
            fullWidth
            onChange={handleNewSkipRule}
          >
            <ToggleButton
              size="small"
              value={SkipRuleType.NONE}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.NONE, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVEN}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVEN, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.ODD}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.ODD, isBigScreen)}
            </ToggleButton>
            <ToggleButton
              size="small"
              value={SkipRuleType.EVERY}
              disabled={!props.inputsEnabled}
            >
              {skipRuleTypeName(SkipRuleType.EVERY, isBigScreen)}
            </ToggleButton>
          </ToggleButtonGroup>
          {everyBlock}
          <input
            type="hidden"
            name={props.name}
            value={assembleSkipRule(editingInfoToSkipRule(editingInfo))}
          />
        </Stack>
      );
  }
}
