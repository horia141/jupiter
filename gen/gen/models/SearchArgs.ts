/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { NamedEntityTag } from './NamedEntityTag';

export type SearchArgs = {
    query: string;
    limit: number;
    include_archived?: boolean;
    filter_entity_tags?: Array<NamedEntityTag>;
};

