/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
/**
 * A quote.
 */
export type QuoteBlock = {
    correlation_id: CorrelationId;
    kind: QuoteBlock.kind;
    text: string;
};
export namespace QuoteBlock {
    export enum kind {
        QUOTE = 'quote',
    }
}

