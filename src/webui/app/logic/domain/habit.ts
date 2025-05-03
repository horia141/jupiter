import {
  HabitSummary,
  ProjectSummary,
  type Habit,
} from "@jupiter/webapi-client";

import { compareDifficulty } from "~/logic/domain/difficulty";
import { compareEisen } from "~/logic/domain/eisen";
import { comparePeriods } from "~/logic/domain/period";

export function sortHabitsNaturally(habits: Habit[]): Habit[] {
  return [...habits].sort((c1, c2) => {
    if (!c1.suspended && c2.suspended) {
      return -1;
    } else if (c1.suspended && !c2.suspended) {
      return 1;
    }

    return (
      comparePeriods(c1.gen_params.period, c2.gen_params.period) ||
      compareEisen(c1.gen_params.eisen, c2.gen_params.eisen) ||
      compareDifficulty(c1.gen_params.difficulty, c2.gen_params.difficulty)
    );
  });
}

export function sortHabitSummariesByProjectAndPeriod(
  habits: HabitSummary[],
  sortedProjects: ProjectSummary[],
): HabitSummary[] {
  return [...habits].sort((c1, c2) => {
    const project1 = sortedProjects.findIndex(
      (p) => p.ref_id === c1.project_ref_id,
    );
    const project2 = sortedProjects.findIndex(
      (p) => p.ref_id === c2.project_ref_id,
    );
    if (project1 !== project2) {
      return project1 - project2;
    }
    return comparePeriods(c1.period, c2.period);
  });
}

export function sortHabitSummariesByPeriod(
  habits: HabitSummary[],
): HabitSummary[] {
  return [...habits].sort((c1, c2) => {
    return comparePeriods(c1.period, c2.period);
  });
}
