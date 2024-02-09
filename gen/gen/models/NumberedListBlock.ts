/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
import type { ListItem } from './ListItem';
export type NumberedListBlock = {
    correlation_id: CorrelationId;
    kind: NumberedListBlock.kind;
    items: Array<ListItem>;
};
export namespace NumberedListBlock {
    export enum kind {
        NUMBERED_LIST = 'numbered-list',
    }
}

