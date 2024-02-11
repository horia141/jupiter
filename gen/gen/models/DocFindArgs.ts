/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * DocFind args.
 */
export type DocFindArgs = {
    include_notes: boolean;
    allow_archived: boolean;
    include_subdocs: boolean;
    filter_ref_ids?: Array<EntityId>;
};

