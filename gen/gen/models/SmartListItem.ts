/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { Timestamp } from './Timestamp';
import type { URL } from './URL';

export type SmartListItem = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    smart_list_ref_id: EntityId;
    is_done: boolean;
    tags_ref_id: Array<EntityId>;
    url: URL;
};

