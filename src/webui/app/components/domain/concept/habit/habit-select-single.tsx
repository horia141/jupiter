import type { EntityId, HabitSummary } from "@jupiter/webapi-client";
import { Autocomplete, TextField } from "@mui/material";
import { useEffect, useMemo, useState } from "react";

interface HabitSelectSingleProps {
  name: string;
  label: string;
  allowNone?: boolean;
  allHabits: HabitSummary[];
  defaultValue?: EntityId;
  value?: EntityId;
  onChange?: (value: EntityId | undefined) => void;
}

export function HabitSelectSingle(props: HabitSelectSingleProps) {
  const allHabitsByRefId = useMemo(
    () => new Map(props.allHabits.map((h) => [h.ref_id, h])),
    [props.allHabits],
  );

  const allHabitsAsOptions = props.allHabits.map((habit) => ({
    habit_ref_id: habit.ref_id,
    label: habit.name,
  }));

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
          <li {...optionProps} key={option.habit_ref_id || "none"}>
            {option.label}
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
  return {
    habit_ref_id: habitRefId,
    label: habit.name,
  };
}
