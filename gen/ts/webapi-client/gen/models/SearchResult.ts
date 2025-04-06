/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ADate } from './ADate';
import type { SearchMatch } from './SearchMatch';
/**
 * Search result.
 */
export type SearchResult = {
    search_time: ADate;
    matches: Array<SearchMatch>;
};

