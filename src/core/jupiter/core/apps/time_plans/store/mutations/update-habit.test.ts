import type { Habit } from "@jupiter/webapi-client";
import {
  Difficulty,
  Eisen,
  HabitRepeatsStrategy,
  RecurringTaskPeriod,
  Schedulability,
} from "@jupiter/webapi-client";
import { describe, expect, it } from "vitest";

import {
  UPDATE_HABIT,
  updateHabitArgsFromForm,
} from "#/core/apps/time_plans/store/mutations/update-habit";
import {
  createTimePlanStore,
  seedTimePlanSource,
  selectTimePlanEntities,
} from "#/core/apps/time_plans/store/store";
import {
  DEFAULT_SCHEDULING_EVENT_COUNT,
  DEFAULT_SCHEDULING_EVENT_DURATION_MINS,
} from "#/core/common/scheduling-params";

const MODIFIED = "2026-09-14T10:00:00Z";

function habit(fields: Partial<Habit> = {}): Habit {
  return {
    ref_id: "400",
    version: 1,
    archived: false,
    name: "Stored name",
    aspect_ref_id: "1",
    chapter_ref_id: null,
    goal_ref_id: null,
    stack_ref_id: "40",
    is_key: false,
    gen_params: {
      period: RecurringTaskPeriod.WEEKLY,
      eisen: Eisen.REGULAR,
      difficulty: Difficulty.EASY,
      actionable_from_day: 2,
      due_at_day: 5,
      skip_rule: "odd",
    },
    suspended: false,
    repeats_strategy: null,
    repeats_in_period_count: null,
    last_modified_time: "2026-09-01T00:00:00Z",
    ...fields,
  } as Habit;
}

function editorForm(fields: Record<string, string>): FormData {
  const formData = new FormData();
  const values = {
    RefId: "400",
    Name: "Edited name",
    Stack: "",
    Period: RecurringTaskPeriod.WEEKLY,
    Eisen: Eisen.IMPORTANT,
    Difficulty: Difficulty.HARD,
    ActionableFromDay: "",
    ActionableFromMonth: "",
    DueAtDay: "3",
    DueAtMonth: "",
    SkipRule: "",
    RepeatsStrategy: "none",
    ...fields,
  };
  for (const [name, value] of Object.entries(values)) {
    formData.set(`targetHabit${name}`, value);
  }
  return formData;
}

describe("updateHabitArgsFromForm", () => {
  it("reads the editor's fields", () => {
    const args = updateHabitArgsFromForm(
      editorForm({ IsKey: "on", Stack: "41", Suspended: "on" }),
      MODIFIED,
      "targetHabit",
    );

    expect(args).toEqual({
      refId: "400",
      name: "Edited name",
      lifePlan: null,
      stackRefId: "41",
      isKey: true,
      genParams: {
        eisen: Eisen.IMPORTANT,
        difficulty: Difficulty.HARD,
        actionableFromDay: null,
        actionableFromMonth: null,
        dueAtDay: 3,
        dueAtMonth: null,
        skipRule: null,
      },
      schedulingParams: {
        schedulability: Schedulability.SCHEDULABLE,
        eventDurationMins: DEFAULT_SCHEDULING_EVENT_DURATION_MINS,
        eventCount: DEFAULT_SCHEDULING_EVENT_COUNT,
      },
      repeatsStrategy: null,
      repeatsInPeriodCount: null,
      suspended: true,
      modifiedTime: MODIFIED,
    });
  });

  it("only takes a repeat count along with a strategy", () => {
    const args = updateHabitArgsFromForm(
      editorForm({
        RepeatsStrategy: HabitRepeatsStrategy.ALL_SAME,
        RepeatsInPeriodCount: "3",
      }),
      MODIFIED,
      "targetHabit",
    );

    expect(args.repeatsStrategy).toBe(HabitRepeatsStrategy.ALL_SAME);
    expect(args.repeatsInPeriodCount).toBe(3);
  });
});

describe("UPDATE_HABIT", () => {
  it("patches the habit, keeping its period", () => {
    const args = updateHabitArgsFromForm(
      editorForm({}),
      MODIFIED,
      "targetHabit",
    );
    const entities = UPDATE_HABIT.applyOptimistic(
      selectTimePlanEntities(
        seedTimePlanSource(createTimePlanStore(), "plan", {
          habits: [habit()],
        }),
      ),
      args,
    );

    expect(entities.habits["400"]).toMatchObject({
      name: "Edited name",
      aspect_ref_id: "1",
      stack_ref_id: null,
      gen_params: {
        period: RecurringTaskPeriod.WEEKLY,
        eisen: Eisen.IMPORTANT,
        actionable_from_day: null,
        due_at_day: 3,
        skip_rule: null,
      },
      last_modified_time: MODIFIED,
    });
  });

  it("sends back what it read", () => {
    const formData = editorForm({ IsKey: "on", DueAtMonth: "2" });
    const args = updateHabitArgsFromForm(formData, MODIFIED, "targetHabit");
    const resent = new FormData();
    for (const [name, value] of Object.entries(
      UPDATE_HABIT.toFormFields(args),
    )) {
      resent.set(
        `targetHabit${name.charAt(0).toUpperCase()}${name.slice(1)}`,
        value,
      );
    }

    expect(updateHabitArgsFromForm(resent, MODIFIED, "targetHabit")).toEqual(
      args,
    );
  });

  it("merges back the habit", () => {
    const updated = habit({ version: 2 });
    expect(UPDATE_HABIT.toDelta({ updated_habit: updated })).toEqual({
      habits: [updated],
    });
  });
});
