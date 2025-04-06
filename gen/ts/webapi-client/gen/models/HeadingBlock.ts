/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
/**
 * A heading.
 */
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

