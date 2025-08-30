/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { Habit } from './Habit';
import type { HabitStreakMark } from './HabitStreakMark';
import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { Project } from './Project';
/**
 * HabitLoadResult.
 */
export type HabitLoadResult = {
    habit: Habit;
    project: Project;
    inbox_tasks: Array<InboxTask>;
    inbox_tasks_total_cnt: number;
    inbox_tasks_page_size: number;
    streak_marks: Array<HabitStreakMark>;
    streak_mark_earliest_date: ADate;
    streak_mark_latest_date: ADate;
    note?: (Note | null);
};

