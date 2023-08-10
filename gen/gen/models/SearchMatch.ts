/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { EntityName } from './EntityName';
import type { NamedEntityTag } from './NamedEntityTag';

export type SearchMatch = {
    entity_tag: NamedEntityTag;
    ref_id: EntityId;
    name: EntityName;
    archived: boolean;
    match_highlight: string;
    match_snippet: string;
    search_rank: number;
};

