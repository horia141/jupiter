/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocName } from './DocName';
import type { EntityId } from './EntityId';
import type { ParentLink } from './ParentLink';
import type { Timestamp } from './Timestamp';
export type Doc = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    name: DocName;
    doc_collection: ParentLink;
    parent_doc_ref_id: EntityId;
};

