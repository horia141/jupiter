/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type HeadingBlock = {
    correlation_id: EntityId;
    kind: HeadingBlock.kind;
    text: string;
};

export namespace HeadingBlock {

    export enum kind {
        HEADING = 'heading',
    }


}

