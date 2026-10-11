import type { Chore, Habit } from "@jupiter/webapi-client";
import {
  Difficulty,
  Eisen,
  HabitRepeatsStrategy,
  RecurringTaskPeriod,
  Schedulability,
} from "@jupiter/webapi-client";
import { describe, expect, it } from "vitest";

import {
  choreEditChangesGeneration,
  habitEditChangesGeneration,
} from "#/core/apps/time_plans/store/regen";
import type { UpdateChoreArgs } from "#/core/apps/time_plans/store/mutations/update-chore";
import type { UpdateHabitArgs } from "#/core/apps/time_plans/store/mutations/update-habit";
import {
  DEFAULT_SCHEDULING_EVENT_COUNT,
  DEFAULT_SCHEDULING_EVENT_DURATION_MINS,
} from "#/core/common/scheduling-params";

const genParams = {
  period: RecurringTaskPeriod.WEEKLY,
  eisen: Eisen.REGULAR,
  difficulty: Difficulty.EASY,
  actionable_from_day: 2,
  due_at_day: 5,
};

const genParamsEdit = {
  eisen: Eisen.REGULAR,
  difficulty: Difficulty.EASY,
  actionableFromDay: 2,
  actionableFromMonth: null,
  dueAtDay: 5,
  dueAtMonth: null,
  skipRule: null,
};

describe("habitEditChangesGeneration", () => {
  const habit = {
    ref_id: "1",
    name: "Run",
    gen_params: genParams,
    repeats_strategy: HabitRepeatsStrategy.ALL_SAME,
    repeats_in_period_count: 3,
    suspended: false,
  } as unknown as Habit;
  const args: UpdateHabitArgs = {
    refId: "1",
    name: "Run",
    lifePlan: null,
    stackRefId: null,
    isKey: false,
    genParams: genParamsEdit,
    repeatsStrategy: HabitRepeatsStrategy.ALL_SAME,
    schedulingParams: {
      schedulability: Schedulability.SCHEDULABLE,
      eventDurationMins: DEFAULT_SCHEDULING_EVENT_DURATION_MINS,
      eventCount: DEFAULT_SCHEDULING_EVENT_COUNT,
    },
    repeatsInPeriodCount: 3,
    suspended: false,
    modifiedTime: "2026-09-14T10:00:00Z",
  };

  it("is false when only the name or other properties change", () => {
    expect(
      habitEditChangesGeneration(habit, {
        ...args,
        name: "Run far",
        isKey: true,
        stackRefId: "9",
      }),
    ).toBe(false);
  });

  it("is true when the gen params change", () => {
    expect(
      habitEditChangesGeneration(habit, {
        ...args,
        genParams: { ...genParamsEdit, eisen: Eisen.IMPORTANT },
      }),
    ).toBe(true);
    expect(
      habitEditChangesGeneration(habit, {
        ...args,
        genParams: { ...genParamsEdit, dueAtDay: 6 },
      }),
    ).toBe(true);
    expect(
      habitEditChangesGeneration(habit, {
        ...args,
        genParams: { ...genParamsEdit, skipRule: "even" },
      }),
    ).toBe(true);
  });

  it("is true when suspending or unsuspending", () => {
    expect(
      habitEditChangesGeneration(habit, { ...args, suspended: true }),
    ).toBe(true);
  });

  it("is true when the repeats change", () => {
    expect(
      habitEditChangesGeneration(habit, { ...args, repeatsInPeriodCount: 4 }),
    ).toBe(true);
    expect(
      habitEditChangesGeneration(habit, {
        ...args,
        repeatsStrategy: null,
        repeatsInPeriodCount: null,
      }),
    ).toBe(true);
  });
});

describe("choreEditChangesGeneration", () => {
  const chore = {
    ref_id: "2",
    name: "Dishes",
    gen_params: genParams,
    must_do: false,
    suspended: false,
    start_at_date: "2026-01-01",
    end_at_date: null,
  } as unknown as Chore;
  const args: UpdateChoreArgs = {
    refId: "2",
    name: "Dishes",
    lifePlan: null,
    stackRefId: null,
    isKey: false,
    genParams: genParamsEdit,
    mustDo: false,
    suspended: false,
    startAtDate: null,
    schedulingParams: {
      schedulability: Schedulability.SCHEDULABLE,
      eventDurationMins: DEFAULT_SCHEDULING_EVENT_DURATION_MINS,
      eventCount: DEFAULT_SCHEDULING_EVENT_COUNT,
    },
    endAtDate: null,
    modifiedTime: "2026-09-14T10:00:00Z",
  };

  it("is false when nothing about generation changes", () => {
    expect(
      choreEditChangesGeneration(chore, { ...args, name: "All the dishes" }),
    ).toBe(false);
    // No start date means leave it alone.
    expect(choreEditChangesGeneration(chore, args)).toBe(false);
    expect(
      choreEditChangesGeneration(chore, { ...args, startAtDate: "2026-01-01" }),
    ).toBe(false);
  });

  it("is true when the gen params, must do or dates change", () => {
    expect(
      choreEditChangesGeneration(chore, {
        ...args,
        genParams: { ...genParamsEdit, difficulty: Difficulty.HARD },
      }),
    ).toBe(true);
    expect(choreEditChangesGeneration(chore, { ...args, mustDo: true })).toBe(
      true,
    );
    expect(
      choreEditChangesGeneration(chore, { ...args, suspended: true }),
    ).toBe(true);
    expect(
      choreEditChangesGeneration(chore, { ...args, startAtDate: "2026-02-01" }),
    ).toBe(true);
    expect(
      choreEditChangesGeneration(chore, { ...args, endAtDate: "2026-12-31" }),
    ).toBe(true);
  });
});
