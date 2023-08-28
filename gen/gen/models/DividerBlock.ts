/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type DividerBlock = {
    correlation_id: EntityId;
    kind: DividerBlock.kind;
};

export namespace DividerBlock {

    export enum kind {
        DIVIDER = 'divider',
    }


}

