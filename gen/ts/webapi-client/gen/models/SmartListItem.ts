/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { SmartListItemName } from './SmartListItemName';
import type { Timestamp } from './Timestamp';
import type { URL } from './URL';
/**
 * A smart list item.
 */
export type SmartListItem = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    archival_reason?: (string | null);
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: SmartListItemName;
    smart_list_ref_id: string;
    is_done: boolean;
    tags_ref_id: Array<EntityId>;
    url?: (URL | null);
};

