/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CorrelationId } from './CorrelationId';

export type ParagraphBlock = {
    correlation_id: CorrelationId;
    kind: ParagraphBlock.kind;
    text: string;
};

export namespace ParagraphBlock {

    export enum kind {
        PARAGRAPH = 'paragraph',
    }


}

