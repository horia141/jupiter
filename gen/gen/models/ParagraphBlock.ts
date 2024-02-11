/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
/**
 * A paragraph of text.
 */
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

