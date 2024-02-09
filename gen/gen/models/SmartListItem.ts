/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { ParentLink } from './ParentLink';
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
    smart_list: ParentLink;
    is_done: boolean;
    tags_ref_id: Array<EntityId>;
    url: URL;
};

