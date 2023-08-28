/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type NumberedListBlock = {
    correlation_id: EntityId;
    kind: NumberedListBlock.kind;
    items: Array<string>;
};

export namespace NumberedListBlock {

    export enum kind {
        NUMBERED_LIST = 'numbered-list',
    }


}

