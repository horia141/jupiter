/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { TagName } from './TagName';
import type { Timestamp } from './Timestamp';

export type SmartListTag = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    tag_name: TagName;
    smart_list_ref_id: EntityId;
};

