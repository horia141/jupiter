/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityIcon } from './EntityIcon';
import type { EntityId } from './EntityId';
import type { SmartListName } from './SmartListName';
import type { Timestamp } from './Timestamp';

/**
 * A smart list.
 */
export type SmartList = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    name: SmartListName;
    smart_list_collection: string;
    icon?: EntityIcon;
};

