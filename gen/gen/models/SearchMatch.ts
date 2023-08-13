/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { NamedEntityTag } from './NamedEntityTag';
import type { Timestamp } from './Timestamp';

export type SearchMatch = {
    entity_tag: NamedEntityTag;
    parent_ref_id: EntityId;
    ref_id: EntityId;
    name: EntityName;
    archived: boolean;
    created_time: Timestamp;
    last_modified_time: Timestamp;
    archived_time: Timestamp;
    match_highlight: string;
    match_snippet: string;
    search_rank: number;
};

