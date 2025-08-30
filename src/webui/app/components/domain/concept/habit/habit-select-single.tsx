import type {
  EntityId,
  HabitSummary,
  ProjectSummary,
} from "@jupiter/webapi-client";
import { Autocomplete, TextField } from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import { PeriodTag } from "~/components/domain/core/period-tag";
import {
  sortHabitSummariesByPeriod,
  sortHabitSummariesByProjectAndPeriod,
} from "~/logic/domain/habit";
import {
  computeProjectHierarchicalNameFromRoot,
  sortProjectsByTreeOrder,
} from "~/logic/domain/project";

interface HabitSelectSingleProps {
  name: string;
  label: string;
  allowNone?: boolean;
  allHabits: HabitSummary[];
  groupByProjects?: boolean;
  allProjects?: ProjectSummary[];
  defaultValue?: EntityId;
  value?: EntityId;
  onChange?: (value: EntityId | undefined) => void;
}

export function HabitSelectSingle(props: HabitSelectSingleProps) {
  const allHabitsByRefId = useMemo(
    () => new Map(props.allHabits.map((h) => [h.ref_id, h])),
    [props.allHabits],
  );

  const sortedProjects =
    props.groupByProjects && props.allProjects
      ? sortProjectsByTreeOrder(props.allProjects)
      : undefined;
  const allProjectsByRefId =
    props.groupByProjects && props.allProjects
      ? new Map(props.allProjects.map((p) => [p.ref_id, p]))
      : undefined;
  const sortedHabits = props.groupByProjects
    ? sortHabitSummariesByProjectAndPeriod(props.allHabits, sortedProjects!)
    : sortHabitSummariesByPeriod(props.allHabits);

  const allHabitsAsOptions = sortedHabits.map(habitToOption);

  const [selectedHabit, setSelectedHabit] = useState(
    selectedHabitToOption(props.value, props.defaultValue, allHabitsByRefId),
  );
  useEffect(() => {
    setSelectedHabit(
      selectedHabitToOption(props.value, props.defaultValue, allHabitsByRefId),
    );
  }, [
    props.allowNone,
    props.value,
    props.defaultValue,
    props.allHabits,
    allHabitsByRefId,
  ]);

  return (
    <>
      <Autocomplete
        autoHighlight
        disableClearable={!props.allowNone}
        groupBy={
          props.groupByProjects && allProjectsByRefId
            ? (option) =>
                computeProjectHierarchicalNameFromRoot(
                  allProjectsByRefId.get(option.project_ref_id)!,
                  allProjectsByRefId,
                )
            : undefined
        }
        id={props.name}
        options={allHabitsAsOptions}
        value={selectedHabit}
        onChange={(e, v) => {
          if (!props.allowNone && !v) {
            return;
          }

          setSelectedHabit(v || undefined);
          if (props.onChange) {
            props.onChange(v?.habit_ref_id);
          }
        }}
        isOptionEqualToValue={(o, v) =>
          (o === undefined && v === undefined) ||
          o?.habit_ref_id === v?.habit_ref_id
        }
        getOptionLabel={(option) => option?.label || ""}
        renderOption={(optionProps, option) => (
          <li
            {...optionProps}
            key={option.habit_ref_id || "none"}
            style={{ display: "flex", alignItems: "center", gap: 1 }}
          >
            {option.label} <PeriodTag period={option.period} />
          </li>
        )}
        renderInput={(params) => <TextField {...params} label={props.label} />}
      />
      <input
        type="hidden"
        name={props.name}
        value={selectedHabit?.habit_ref_id || ""}
      />
    </>
  );
}

function selectedHabitToOption(
  value: EntityId | undefined,
  defaultValue: EntityId | undefined,
  allHabitsByRefId: Map<EntityId, HabitSummary>,
) {
  const habitRefId = value || defaultValue;
  const habit = habitRefId ? allHabitsByRefId.get(habitRefId) : undefined;

  if (habitRefId === undefined || habit === undefined) {
    return undefined;
  }
  return habitToOption(habit);
}

function habitToOption(habit: HabitSummary) {
  return {
    habit_ref_id: habit.ref_id,
    label: habit.name,
    period: habit.period,
    project_ref_id: habit.project_ref_id,
  };
}
