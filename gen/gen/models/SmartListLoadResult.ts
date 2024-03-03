/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { SmartList } from './SmartList';
import type { SmartListItem } from './SmartListItem';
import type { SmartListTag } from './SmartListTag';

/**
 * SmartListLoadResult.
 */
export type SmartListLoadResult = {
    smart_list: SmartList;
    smart_list_tags: Array<SmartListTag>;
    smart_list_items: Array<SmartListItem>;
};

