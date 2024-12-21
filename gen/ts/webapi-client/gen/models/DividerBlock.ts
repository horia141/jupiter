/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CorrelationId } from './CorrelationId';

/**
 * A divider.
 */
export type DividerBlock = {
    correlation_id: CorrelationId;
    kind: DividerBlock.kind;
};

export namespace DividerBlock {

    export enum kind {
        DIVIDER = 'divider',
    }


}

