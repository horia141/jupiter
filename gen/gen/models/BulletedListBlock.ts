/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { ListItem } from './ListItem';

export type BulletedListBlock = {
    correlation_id: EntityId;
    kind: BulletedListBlock.kind;
    items: Array<ListItem>;
};

export namespace BulletedListBlock {

    export enum kind {
        BULLETED_LIST = 'bulleted-list',
    }


}

