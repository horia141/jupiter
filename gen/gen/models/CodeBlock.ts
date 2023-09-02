/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';

export type CodeBlock = {
    correlation_id: EntityId;
    kind: CodeBlock.kind;
    code: string;
    language?: string;
    show_line_numbers?: boolean;
};

export namespace CodeBlock {

    export enum kind {
        CODE = 'code',
    }


}

