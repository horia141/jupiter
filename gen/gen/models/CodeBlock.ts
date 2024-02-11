/* generated using openapi-typescript-codegen -- do no edit */
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
    language?: string;
    show_line_numbers?: boolean;
};
export namespace CodeBlock {
    export enum kind {
        CODE = 'code',
    }
}

