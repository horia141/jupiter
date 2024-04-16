/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { SmartListItem } from './SmartListItem';
import type { SmartListTag } from './SmartListTag';

/**
 * SmartListItemLoadResult.
 */
export type SmartListItemLoadResult = {
    item: SmartListItem;
    tags: Array<SmartListTag>;
    note?: Note;
};

