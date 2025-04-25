/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Journal } from './Journal';
import type { JournalStats } from './JournalStats';
/**
 * Result.
 */
export type JournalLoadForDateAndPeriodResult = {
    journal?: (Journal | null);
    journal_stats?: (JournalStats | null);
    sub_period_journals: Array<Journal>;
};

