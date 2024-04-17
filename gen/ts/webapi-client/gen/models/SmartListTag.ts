/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { TagName } from './TagName';
import type { Timestamp } from './Timestamp';

/**
 * A smart list tag.
 */
export type SmartListTag = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: EntityName;
    smart_list_ref_id: string;
    tag_name: TagName;
};

