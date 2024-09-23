/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EventSource } from './EventSource';

/**
 * ScheduleExternalSyncDoArgs.
 */
export type ScheduleExternalSyncDoArgs = {
    source: EventSource;
    sync_even_if_not_modified: boolean;
    filter_schedule_stream_ref_id?: (Array<EntityId> | null);
};

