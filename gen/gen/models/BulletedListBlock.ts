/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CorrelationId } from './CorrelationId';
import type { ListItem } from './ListItem';

export type BulletedListBlock = {
    correlation_id: CorrelationId;
    kind: BulletedListBlock.kind;
    items: Array<ListItem>;
};

export namespace BulletedListBlock {

    export enum kind {
        BULLETED_LIST = 'bulleted-list',
    }


}

