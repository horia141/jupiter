/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { EntitySummary } from './EntitySummary';
import type { EventSource } from './EventSource';
import type { ParentLink } from './ParentLink';
import type { SyncTarget } from './SyncTarget';
import type { Timestamp } from './Timestamp';
export type GCLogEntry = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    gc_log: ParentLink;
    source: EventSource;
    gc_targets: Array<SyncTarget>;
    opened: boolean;
    entity_records: Array<EntitySummary>;
};

