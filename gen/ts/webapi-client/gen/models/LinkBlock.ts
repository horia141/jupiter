/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CorrelationId } from './CorrelationId';
import type { URL } from './URL';
/**
 * A link.
 */
export type LinkBlock = {
    correlation_id: CorrelationId;
    kind: LinkBlock.kind;
    url: URL;
};
export namespace LinkBlock {
    export enum kind {
        LINK = 'link',
    }
}

