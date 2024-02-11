/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SmartList } from './SmartList';
import type { SmartListItem } from './SmartListItem';
import type { SmartListTag } from './SmartListTag';
/**
 * A single entry in the LoadAllSmartListsResponse.
 */
export type SmartListFindResponseEntry = {
    smart_list: SmartList;
    smart_list_tags?: Array<SmartListTag>;
    smart_list_items?: Array<SmartListItem>;
};

