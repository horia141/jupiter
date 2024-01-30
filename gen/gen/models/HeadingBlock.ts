/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CorrelationId } from './CorrelationId';

export type HeadingBlock = {
    correlation_id: CorrelationId;
    kind: HeadingBlock.kind;
    text: string;
    level: number;
};

export namespace HeadingBlock {

    export enum kind {
        HEADING = 'heading',
    }


}

