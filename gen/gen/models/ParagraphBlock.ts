/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type ParagraphBlock = {
    correlation_id: EntityId;
    kind: ParagraphBlock.kind;
    text: string;
};

export namespace ParagraphBlock {

    export enum kind {
        PARAGRAPH = 'paragraph',
    }


}

