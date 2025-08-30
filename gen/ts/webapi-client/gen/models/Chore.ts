/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { ChoreName } from './ChoreName';
import type { EntityId } from './EntityId';
import type { RecurringTaskGenParams } from './RecurringTaskGenParams';
import type { Timestamp } from './Timestamp';
/**
 * A chore.
 */
export type Chore = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: ChoreName;
    chore_collection_ref_id: string;
    project_ref_id: EntityId;
    is_key: boolean;
    gen_params: RecurringTaskGenParams;
    suspended: boolean;
    must_do: boolean;
    start_at_date: ADate;
    end_at_date?: (ADate | null);
};

