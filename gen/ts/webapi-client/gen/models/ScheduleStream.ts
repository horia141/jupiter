/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ScheduleStreamColor } from './ScheduleStreamColor';
import type { ScheduleStreamName } from './ScheduleStreamName';
import type { ScheduleStreamSource } from './ScheduleStreamSource';
import type { Timestamp } from './Timestamp';
import type { URL } from './URL';

/**
 * A schedule group or stream of events.
 */
export type ScheduleStream = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: ScheduleStreamName;
    schedule_domain_ref_id: string;
    source: ScheduleStreamSource;
    color: ScheduleStreamColor;
    source_ical_url?: (URL | null);
};
