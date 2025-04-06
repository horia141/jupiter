/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';
import type { VacationName } from './VacationName';
/**
 * A vacation.
 */
export type Vacation = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: VacationName;
    vacation_collection_ref_id: string;
    start_date: ADate;
    end_date: ADate;
};

