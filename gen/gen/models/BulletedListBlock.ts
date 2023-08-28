/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type BulletedListBlock = {
    correlation_id: EntityId;
    kind: BulletedListBlock.kind;
    items: Array<string>;
};

export namespace BulletedListBlock {

    export enum kind {
        BULLETED_LIST = 'bulleted-list',
    }


}

