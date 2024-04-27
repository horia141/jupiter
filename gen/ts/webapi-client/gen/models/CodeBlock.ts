/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CorrelationId } from './CorrelationId';

/**
 * A code block.
 */
export type CodeBlock = {
    correlation_id: CorrelationId;
    kind: CodeBlock.kind;
    code: string;
    language?: (string | null);
    show_line_numbers?: (boolean | null);
};

export namespace CodeBlock {

    export enum kind {
        CODE = 'code',
    }


}

