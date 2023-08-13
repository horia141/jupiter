/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { NamedEntityTag } from './NamedEntityTag';
import type { SearchLimit } from './SearchLimit';
import type { SearchQuery } from './SearchQuery';

export type SearchArgs = {
    query: SearchQuery;
    limit: SearchLimit;
    include_archived?: boolean;
    filter_entity_tags?: Array<NamedEntityTag>;
};

