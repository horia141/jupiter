/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Person } from './Person';
import type { ScheduleEventFullDays } from './ScheduleEventFullDays';
import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';
import type { Vacation } from './Vacation';
/**
 * FullDaysBlockLoadResult.
 */
export type TimeEventFullDaysBlockLoadResult = {
    full_days_block: TimeEventFullDaysBlock;
    schedule_event?: (ScheduleEventFullDays | null);
    person?: (Person | null);
    vacation?: (Vacation | null);
};

