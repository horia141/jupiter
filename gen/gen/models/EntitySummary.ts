/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { NamedEntityTag } from './NamedEntityTag';
import type { Timestamp } from './Timestamp';
/**
 * Information about a particular entity very broadly.
 */
export type EntitySummary = {
    entity_tag: NamedEntityTag;
    parent_ref_id: EntityId;
    ref_id: EntityId;
    name: EntityName;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time?: Timestamp;
    snippet: string;
};

