/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EventSource } from './EventSource';

/**
 * ScheduleExternalSyncDoArgs.
 */
export type ScheduleExternalSyncDoArgs = {
    source: EventSource;
    today?: (ADate | null);
    sync_even_if_not_modified: boolean;
    filter_schedule_stream_ref_id?: (Array<EntityId> | null);
};

