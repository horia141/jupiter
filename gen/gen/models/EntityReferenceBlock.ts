/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EntityId } from './EntityId';
import type { NamedEntityTag } from './NamedEntityTag';

export type EntityReferenceBlock = {
    correlation_id: EntityId;
    kind: EntityReferenceBlock.kind;
    entity_tag: NamedEntityTag;
    ref_id: EntityId;
};

export namespace EntityReferenceBlock {

    export enum kind {
        ENTITY_REFERENCE = 'entity-reference',
    }


}
