/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { Timestamp } from './Timestamp';

export type Doc = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: EntityName;
    doc_collection_ref_id: EntityId;
    parent_doc_ref_id: EntityId;
};

