/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type TableBlock = {
    correlation_id: EntityId;
    kind: TableBlock.kind;
    with_header: boolean;
    contents: Array<Array<string>>;
};

export namespace TableBlock {

    export enum kind {
        TABLE = 'table',
    }


}

