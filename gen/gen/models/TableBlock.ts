/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
export type TableBlock = {
    correlation_id: CorrelationId;
    kind: TableBlock.kind;
    with_header: boolean;
    contents: Array<Array<string>>;
};
export namespace TableBlock {
    export enum kind {
        TABLE = 'table',
    }
}

