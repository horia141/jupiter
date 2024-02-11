/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityId } from './EntityId';
/**
 * PersonFindArgs.
 */
export type PersonFindArgs = {
    allow_archived: boolean;
    include_catch_up_inbox_tasks: boolean;
    include_birthday_inbox_tasks: boolean;
    include_notes: boolean;
    filter_person_ref_ids?: Array<EntityId>;
};

