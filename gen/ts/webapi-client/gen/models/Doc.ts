/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocName } from './DocName';
import type { EntityId } from './EntityId';
import type { Timestamp } from './Timestamp';
/**
 * A doc in the docbook.
 */
export type Doc = {
    ref_id: EntityId;
    version: number;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: (Timestamp | null);
    name: DocName;
    doc_collection_ref_id: string;
    parent_doc_ref_id?: (EntityId | null);
};

