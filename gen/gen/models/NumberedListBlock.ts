/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ListItem } from './ListItem';

export type NumberedListBlock = {
    correlation_id: EntityId;
    kind: NumberedListBlock.kind;
    items: Array<ListItem>;
};

export namespace NumberedListBlock {

    export enum kind {
        NUMBERED_LIST = 'numbered-list',
    }


}

