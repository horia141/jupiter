import type { Chore } from "@jupiter/webapi-client";
import { Difficulty, Eisen, RecurringTaskPeriod } from "@jupiter/webapi-client";
import { describe, expect, it } from "vitest";

import {
  UPDATE_CHORE,
  updateChoreArgsFromForm,
} from "#/core/apps/time_plans/store/mutations/update-chore";
import {
  createTimePlanStore,
  seedTimePlanSource,
  selectTimePlanEntities,
} from "#/core/apps/time_plans/store/store";

const MODIFIED = "2026-09-14T10:00:00Z";

function chore(fields: Partial<Chore> = {}): Chore {
  return {
    ref_id: "600",
    version: 1,
    archived: false,
    name: "Stored name",
    aspect_ref_id: "1",
    chapter_ref_id: null,
    goal_ref_id: null,
    stack_ref_id: null,
    is_key: false,
    gen_params: {
      period: RecurringTaskPeriod.MONTHLY,
      eisen: Eisen.REGULAR,
      difficulty: Difficulty.EASY,
    },
    suspended: false,
    must_do: true,
    start_at_date: "2026-01-01",
    end_at_date: "2026-12-31",
    last_modified_time: "2026-09-01T00:00:00Z",
    ...fields,
  } as Chore;
}

function editorForm(fields: Record<string, string>): FormData {
  const formData = new FormData();
  const values = {
    RefId: "600",
    Name: "Edited name",
    Stack: "60",
    Period: RecurringTaskPeriod.MONTHLY,
    Eisen: Eisen.IMPORTANT,
    Difficulty: Difficulty.HARD,
    DueAtDay: "15",
    SkipRule: "",
    StartAtDate: "",
    EndAtDate: "",
    ...fields,
  };
  for (const [name, value] of Object.entries(values)) {
    formData.set(`targetChore${name}`, value);
  }
  return formData;
}

describe("updateChoreArgsFromForm", () => {
  it("reads the editor's fields", () => {
    const args = updateChoreArgsFromForm(
      editorForm({
        Aspect: "2",
        MustDo: "on",
        Suspended: "on",
        StartAtDate: "2026-02-01",
      }),
      MODIFIED,
      "targetChore",
    );

    expect(args).toMatchObject({
      refId: "600",
      name: "Edited name",
      lifePlan: { aspectRefId: "2", chapterRefId: null, goalRefId: null },
      stackRefId: "60",
      isKey: false,
      mustDo: true,
      suspended: true,
      startAtDate: "2026-02-01",
      endAtDate: null,
    });
    expect(args.genParams.dueAtDay).toBe(15);
  });
});

describe("UPDATE_CHORE", () => {
  it("keeps the start date when none was picked, but clears the end date", () => {
    const entities = UPDATE_CHORE.applyOptimistic(
      selectTimePlanEntities(
        seedTimePlanSource(createTimePlanStore(), "plan", {
          chores: [chore()],
        }),
      ),
      updateChoreArgsFromForm(editorForm({}), MODIFIED, "targetChore"),
    );

    expect(entities.chores["600"]).toMatchObject({
      name: "Edited name",
      stack_ref_id: "60",
      must_do: false,
      start_at_date: "2026-01-01",
      end_at_date: null,
      gen_params: { period: RecurringTaskPeriod.MONTHLY, due_at_day: 15 },
      last_modified_time: MODIFIED,
    });
  });

  it("sends the must do flag the way a switch does", () => {
    const args = updateChoreArgsFromForm(
      editorForm({ MustDo: "on" }),
      MODIFIED,
      "targetChore",
    );
    expect(UPDATE_CHORE.toFormFields(args).mustDo).toBe("on");
    expect(
      UPDATE_CHORE.toFormFields({ ...args, mustDo: false }),
    ).not.toHaveProperty("mustDo");
  });

  it("merges back the chore", () => {
    const updated = chore({ version: 2 });
    expect(UPDATE_CHORE.toDelta({ updated_chore: updated })).toEqual({
      chores: [updated],
    });
  });
});
