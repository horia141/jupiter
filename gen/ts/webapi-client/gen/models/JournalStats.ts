/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReportPeriodResult } from './ReportPeriodResult';
import type { Timestamp } from './Timestamp';
/**
 * Stats about a journal.
 */
export type JournalStats = {
    created_time: Timestamp;
    last_modified_time: Timestamp;
    journal_ref_id: string;
    report: ReportPeriodResult;
};

