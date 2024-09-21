/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { TimeEventNamespace } from './TimeEventNamespace';
import type { TimeInDay } from './TimeInDay';
import type { Timestamp } from './Timestamp';

/**
 * Time event.
 */
export type TimeEventInDayBlock = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    time_event_domain_ref_id: string;
    namespace: TimeEventNamespace;
    source_entity_ref_id: EntityId;
    start_date: ADate;
    start_time_in_day: TimeInDay;
    duration_mins: number;
};

