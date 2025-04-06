/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Note } from './Note';
import type { SmartList } from './SmartList';
import type { SmartListItem } from './SmartListItem';
import type { SmartListTag } from './SmartListTag';
/**
 * A single entry in the LoadAllSmartListsResponse.
 */
export type SmartListFindResponseEntry = {
    smart_list: SmartList;
    note?: (Note | null);
    smart_list_tags?: (Array<SmartListTag> | null);
    smart_list_items?: (Array<SmartListItem> | null);
    smart_list_item_notes?: (Array<Note> | null);
};

