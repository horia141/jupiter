/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { NamedEntityTag } from './NamedEntityTag';
import type { SearchLimit } from './SearchLimit';
import type { SearchQuery } from './SearchQuery';
/**
 * Search args.
 */
export type SearchArgs = {
    query: SearchQuery;
    limit: SearchLimit;
    include_archived: boolean;
    filter_entity_tags?: (Array<NamedEntityTag> | null);
    filter_created_time_after?: (ADate | null);
    filter_created_time_before?: (ADate | null);
    filter_last_modified_time_after?: (ADate | null);
    filter_last_modified_time_before?: (ADate | null);
    filter_archived_time_after?: (ADate | null);
    filter_archived_time_before?: (ADate | null);
};

