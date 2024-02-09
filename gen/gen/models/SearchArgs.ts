/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { NamedEntityTag } from './NamedEntityTag';
import type { SearchLimit } from './SearchLimit';
import type { SearchQuery } from './SearchQuery';
export type SearchArgs = {
    query: SearchQuery;
    limit: SearchLimit;
    include_archived: boolean;
    filter_entity_tags?: Array<NamedEntityTag>;
    filter_created_time_after?: ADate;
    filter_created_time_before?: ADate;
    filter_last_modified_time_after?: ADate;
    filter_last_modified_time_before?: ADate;
    filter_archived_time_after?: ADate;
    filter_archived_time_before?: ADate;
};

