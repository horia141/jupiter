/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { URL } from './URL';

export type LinkBlock = {
    correlation_id: EntityId;
    kind: LinkBlock.kind;
    url: URL;
};

export namespace LinkBlock {

    export enum kind {
        LINK = 'link',
    }


}

