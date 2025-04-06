/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
import type { ListItem } from './ListItem';
/**
 * A numbered list.
 */
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

