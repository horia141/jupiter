/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChecklistItem } from './ChecklistItem';
import type { CorrelationId } from './CorrelationId';

/**
 * A todo list.
 */
export type ChecklistBlock = {
    correlation_id: CorrelationId;
    kind: ChecklistBlock.kind;
    items: Array<ChecklistItem>;
};

export namespace ChecklistBlock {

    export enum kind {
        CHECKLIST = 'checklist',
    }


}

