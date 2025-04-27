/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { InboxTaskStatus } from './InboxTaskStatus';
import type { Timestamp } from './Timestamp';
/**
 * The record of a streak of a habit.
 */
export type HabitStreakMark = {
    created_time: Timestamp;
    last_modified_time: Timestamp;
    habit_ref_id: string;
    year: number;
    date: ADate;
    statuses: Record<string, InboxTaskStatus>;
};

