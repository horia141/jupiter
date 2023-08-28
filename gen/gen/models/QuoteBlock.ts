/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type QuoteBlock = {
    correlation_id: EntityId;
    kind: QuoteBlock.kind;
    text: string;
};

export namespace QuoteBlock {

    export enum kind {
        QUOTE = 'quote',
    }


}

