/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChecklistItem } from './ChecklistItem';
import type { EntityId } from './EntityId';

export type ChecklistBlock = {
    correlation_id: EntityId;
    kind: ChecklistBlock.kind;
    items: Array<ChecklistItem>;
};

export namespace ChecklistBlock {

    export enum kind {
        CHECKLIST = 'checklist',
    }


}

